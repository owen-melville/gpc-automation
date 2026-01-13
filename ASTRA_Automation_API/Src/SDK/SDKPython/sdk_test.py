# -*- coding: utf-8 -*-

"""
ASTRA AUTOMATION API unit tests for Python

The tests name have to start with "test_[number]", where number indicate the order of the code being executed.
"""

import os
import unittest

import comtypes
import comtypes.safearray

from astra_admin import AstraAdmin, BaselineType, SampleInfo
from sdk_helper import SdkHelper
from known_path import KnownPaths
from pathlib import Path
from ctypes import *

admin = AstraAdmin()

class A_SdkUnitTests(unittest.TestCase):
    fraction_results_json = [
        '{ "DeviceId":"f9d574e2-84a7-4c8d-964f-c44ffc6abd31","Id":1,"Location":"Vial 1","VolumeSpecified":true,"Volume":0.500667,"StartTime":60.02,"EndTime":90.06,"StartReason":"TimeBasedTimeSlice","EndReason":"Unknown","PeakDetectorInfos":[{"PeakDetector":{"ID":"G7121A:DEAE304354 P","DeviceType":"G7121A","SerialNumber":"DEAE304354"},"DelayTime":0.0,"PeakDetected":false},{"PeakDetector":{"ID":"G7165A:DEAC800888 P","DeviceType":"G7165A","SerialNumber":"DEAC800888"},"DelayTime":0.0,"PeakDetected":true}]}',
        '{ "DeviceId":"f9d574e2-84a7-4c8d-964f-c44ffc6abd31","Id":2,"Location":"Vial 2","VolumeSpecified":true,"Volume":0.494133,"StartTime":90.41,"EndTime":120.06,"StartReason":"TimeBasedTimeSlice","EndReason":"Unknown","PeakDetectorInfos":[{"PeakDetector":{"ID":"G7121A:DEAE304354 P","DeviceType":"G7121A","SerialNumber":"DEAE304354"},"DelayTime":0.0,"PeakDetected":false},{"PeakDetector":{"ID":"G7165A:DEAC800888 P","DeviceType":"G7165A","SerialNumber":"DEAC800888"},"DelayTime":0.0,"PeakDetected":true}]}',
        '{ "DeviceId":"f9d574e2-84a7-4c8d-964f-c44ffc6abd31","Id":3,"Location":"Vial 3","VolumeSpecified":true,"Volume":0.495133,"StartTime":120.35,"EndTime":150.06,"StartReason":"TimeBasedTimeSlice","EndReason":"Unknown","PeakDetectorInfos":[{"PeakDetector":{"ID":"G7121A:DEAE304354 P","DeviceType":"G7121A","SerialNumber":"DEAE304354"},"DelayTime":0.0,"PeakDetected":false},{"PeakDetector":{"ID":"G7165A:DEAC800888 P","DeviceType":"G7165A","SerialNumber":"DEAC800888"},"DelayTime":0.0,"PeakDetected":true}]}',
        '{ "DeviceId":"f9d574e2-84a7-4c8d-964f-c44ffc6abd31","Id":4,"Location":"Vial 4","VolumeSpecified":true,"Volume":0.495533,"StartTime":150.33,"EndTime":180.06,"StartReason":"TimeBasedTimeSlice","EndReason":"Unknown","PeakDetectorInfos":[{"PeakDetector":{"ID":"G7121A:DEAE304354 P","DeviceType":"G7121A","SerialNumber":"DEAE304354"},"DelayTime":0.0,"PeakDetected":false},{"PeakDetector":{"ID":"G7165A:DEAC800888 P","DeviceType":"G7165A","SerialNumber":"DEAC800888"},"DelayTime":0.0,"PeakDetected":true}]}',
        '{ "DeviceId":"f9d574e2-84a7-4c8d-964f-c44ffc6abd31","Id":5,"Location":"Vial 5","VolumeSpecified":true,"Volume":0.496000,"StartTime":180.30,"EndTime":210.06,"StartReason":"TimeBasedTimeSlice","EndReason":"Unknown","PeakDetectorInfos":[{"PeakDetector":{"ID":"G7121A:DEAE304354 P","DeviceType":"G7121A","SerialNumber":"DEAE304354"},"DelayTime":0.0,"PeakDetected":false},{"PeakDetector":{"ID":"G7165A:DEAC800888 P","DeviceType":"G7165A","SerialNumber":"DEAC800888"},"DelayTime":0.0,"PeakDetected":true}]}',
    ]

    def __init__(self, method_name: str = "SdkUnitTests") -> None:
        super().__init__(method_name)

    def test_01_baselines(self):
        SdkHelper().restart_astra_and_wait()
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        baselines = admin.get_baselines(exp_id)

        # GetBaselines
        self.assertEqual(4, len(baselines))

        self.assertEqual("detector1", baselines[0].seriesName)
        self.assertEqual("detector2", baselines[1].seriesName)
        self.assertEqual("detector3", baselines[2].seriesName)
        self.assertEqual("differentialrefractiveindexdata", baselines[3].seriesName)

        self.assertEqual(BaselineType.SNAP_Y.value, baselines[0].type)
        self.assertEqual(BaselineType.SNAP_Y.value, baselines[1].type)
        self.assertEqual(BaselineType.SNAP_Y.value, baselines[2].type)
        self.assertEqual(BaselineType.SNAP_Y.value, baselines[3].type)

        # SetBaselines
        self.assertEqual("4.12813263501398", f"{baselines[0].start.x}"[:16])
        self.assertEqual("37.3603182731067", f"{baselines[0].end.x}"[:16])
        baselines[0].start.x = 0.0
        admin.update_baselines(exp_id, baselines)
        baselines = admin.get_baselines(exp_id)

        self.assertEqual("0.0", f"{baselines[0].start.x}"[:16])

    def test_02_some_baselines_missing(self):
        exp_file_path = KnownPaths().get_experiment_data(
            "30k poly no config or sample_missing baselines.afe7"
        )
        exp_id = admin.open_experiment(exp_file_path)

        baselines = admin.get_baselines(exp_id)

        # GetBaselines and make sure that we have 4 including the none ones.
        self.assertEqual(4, len(baselines))

        self.assertEqual("detector1", baselines[0].seriesName)
        self.assertEqual("detector2", baselines[1].seriesName)
        self.assertEqual("detector3", baselines[2].seriesName)
        self.assertEqual("differentialrefractiveindexdata", baselines[3].seriesName)

        # Make sure the 2 edited baselines are type none still.
        self.assertEqual(BaselineType.SNAP_Y.value, baselines[0].type)
        self.assertEqual(BaselineType.NONE.value, baselines[1].type)
        self.assertEqual(BaselineType.NONE.value, baselines[2].type)
        self.assertEqual(BaselineType.SNAP_Y.value, baselines[3].type)

    def test_03_all_baselines_missing(self):
        exp_file_path = KnownPaths().get_experiment_data(
            "BSA_All Baselines Missing Test Experiment.afe8"
        )
        exp_id = admin.open_experiment(exp_file_path)

        baselines = admin.get_baselines(exp_id)

        # GetBaselines and make sure that we get 18 entries int total
        self.assertEqual(18, len(baselines))

        # Check name
        for i, baseline in enumerate(baselines[:-1]):
            self.assertEqual(f"detector{i+2}", baseline.seriesName)
        self.assertEqual("differentialrefractiveindexdata", baselines[17].seriesName)

        for i, baseline in enumerate(baselines):
            # All entries should have type of None, and have start/end value of 0
            self.assertEqual(BaselineType.NONE.value, baseline.type)
            self.assertEqual("0.0", f"{baseline.start.x}"[:16])
            self.assertEqual("0.0", f"{baseline.end.x}"[:16])

    def test_04_autofind_for_all_baselines_missing(self):
        exp_file_path = KnownPaths().get_experiment_data(
            "BSA_All Baselines Missing Test Experiment.afe8"
        )
        exp_id = admin.open_experiment(exp_file_path)

        admin.set_auto_autofind_baselines(exp_id, True)
        admin.run_experiment(exp_id)
        baselines = admin.get_baselines(exp_id)

        # GetBaselines and make sure that we get 18 entries int total
        self.assertEqual(18, len(baselines))

        # Check name
        for i, baseline in enumerate(baselines[:-1]):
            self.assertEqual(f"detector{i+2}", baseline.seriesName)
        self.assertEqual("differentialrefractiveindexdata", baselines[17].seriesName)

        for i, baseline in enumerate(baselines):
            # All entries should have type of None, and have start/end value of 0
            self.assertEqual(BaselineType.AUTOMATIC.value, baseline.type)

        # Check detector13's start and end values
        self.assertEqual("0.0058666666666666", f"{baselines[11].start.x}"[:18])
        self.assertEqual("0.0090093376872471", f"{baselines[11].start.y}"[:18])

        self.assertEqual("30.000533333333", f"{baselines[11].end.x}"[:15])
        self.assertEqual("0.0090070727314900", f"{baselines[11].end.y}"[:18])

    def test_05_get_data_set(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        # GetDataSet
        definition_name = "mean square radius vs volume"
        results = admin.get_data_set(exp_id, definition_name)
        self.assertTrue(len(results) > 100)

        # SaveDataSet
        data_set_file_path = os.path.join(
            KnownPaths().get_qa_test_data(), r"experiments\30k polystyrene treos + rex data.csv"
        )
        admin.save_data_set(exp_id, definition_name, data_set_file_path)
        self.assertTrue(os.path.exists(data_set_file_path))
        saved_results = Path(data_set_file_path).read_text()
        saved_results = saved_results.replace("\r", "").replace("Â", "")

        self.assertEqual(results, saved_results)

    def test_06_get_results(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        # GetResults
        results = admin.get_results(exp_id)
        index = results.index("3.043288841e+04")
        self.assertNotEqual(-1, index)

        # SaveResults
        results_file_path = os.path.join(
            KnownPaths().get_qa_test_data(), r"experiments\30k polystyrene treos + rex results.txt"
        )
        admin.save_results(exp_id, results_file_path)
        self.assertTrue(os.path.exists(results_file_path))
        results = Path(results_file_path).read_text()
        index = results.index("3.043288841e+04")
        self.assertNotEqual(-1, index)

    def test_07_peaks(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        # GetPeakRanges
        peaks = admin.get_peak_ranges(exp_id)
        self.assertEqual(1, len(peaks))
        self.assertEqual("29.2262894724135", f"{peaks[0].start}"[:16])
        self.assertEqual("31.1766107753454", f"{peaks[0].end}"[:16])

        # AddPeakRange
        admin.add_peak_range(exp_id, 1.1, 2.2)
        peaks = admin.get_peak_ranges(exp_id)
        self.assertEqual("1.1", f"{peaks[1].start}"[:16])
        self.assertEqual("2.2", f"{peaks[1].end}"[:16])

        # UpdatePeakRanges
        self.assertEqual(2, len(peaks))
        peaks[1].start = 11.1
        peaks[1].end = 22.2
        admin.update_peak_range(exp_id, peaks[1])
        peaks = admin.get_peak_ranges(exp_id)
        self.assertEqual("11.1", f"{peaks[1].start}"[:16])
        self.assertEqual("22.2", f"{peaks[1].end}"[:16])

    def test_08_autofind(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        # SetAutoAutofindBaselines
        admin.set_auto_autofind_baselines(exp_id, True)
        baselines = admin.get_baselines(exp_id)

        self.assertEqual(4, len(baselines))
        self.assertEqual("detector1", baselines[0].seriesName)
        self.assertEqual("detector2", baselines[1].seriesName)
        self.assertEqual("detector3", baselines[2].seriesName)
        self.assertEqual("differentialrefractiveindexdata", baselines[3].seriesName)

        self.assertEqual(BaselineType.AUTOMATIC.value, baselines[0].type)
        self.assertEqual(BaselineType.AUTOMATIC.value, baselines[1].type)
        self.assertEqual(BaselineType.AUTOMATIC.value, baselines[2].type)
        self.assertEqual(BaselineType.AUTOMATIC.value, baselines[3].type)

        self.assertEqual("0.0", f"{baselines[0].start.x}"[:16])
        self.assertEqual("39.9820666666666", f"{baselines[0].end.x}"[:16])

        # SetAutoAutofindPeaks
        admin.set_auto_autofind_peaks(exp_id, True)
        peaks = admin.get_peak_ranges(exp_id)

        self.assertEqual(2, len(peaks))
        self.assertEqual("29.2416209684213", f"{peaks[0].start}"[:16])
        self.assertEqual("30.9755800701758", f"{peaks[0].end}"[:16])
        self.assertEqual("25.8915446456141", f"{peaks[1].start}"[:16])
        self.assertEqual("26.3797467228071", f"{peaks[1].end}"[:16])

    def test_09_permission(self):
        database_name = "CI_astra_data"
        guest_username = "swtester_g"
        technician_username = "swtester_t"
        password = "still@SWT!er"
        domain = "wyatt.com"
        # enable security pack
        SdkHelper().enable_security_pack(database_name, guest_username, password)

        # Logon to security pack as guest
        security_pack_active = admin.is_security_pack_active()
        is_logged_in = admin.is_logged_in()

        if security_pack_active and is_logged_in:
            result = admin.validate_logon(guest_username, password, domain)

            # result.isValid return 0 if logon failed, return 1 if succeeded.
            self.assertEqual(1, result.isValid)

            exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
            exp_id = admin.open_experiment(exp_file_path)

            # Guest cannot edit experiments
            success = True
            try:
                admin.add_peak_range(exp_id, 0, 1)
            except Exception:
                success = False
            self.assertFalse(success)

            # logon as technician
            result = admin.validate_logon(technician_username, password, domain)

            # result.isValid return 0 if logon failed, return 1 if succeeded.
            self.assertEqual(1, result.isValid)

            exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
            exp_id = admin.open_experiment(exp_file_path)

            # Technician can edit experiments
            success = False
            try:
                admin.add_peak_range(exp_id, 0, 1)
                success = True
            except Exception:
                success = False
            self.assertTrue(success)

        # Disable security pack
        SdkHelper().disable_security_pack()

    def test_10_error_message_when_file_name_incorrect(self):
        error_encountered = False

        admin.should_show_error_message_box = False
        try:
            exp_file_path = KnownPaths().get_experiment_data("this file does not exist.afe7")
            exp_id = admin.open_experiment(exp_file_path)
        except Exception as ex:
            error_encountered = True

            expected_msg = "Cannot read file. File name may be incorrect. Otherwise, file is either from a new version of ASTRA or corrupt."
            self.assertEqual(expected_msg, ex.args[2][0])
        
        admin.should_show_error_message_box = True

        # Make sure we actually caught the exception
        self.assertTrue(error_encountered)

    def test_11_add_fraction_results(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        success = True
        try:
            # Add the mock fraction results to the experiment dataset
            for i, fraction_result in enumerate(self.fraction_results_json):
                bstr = comtypes.BSTR(fraction_result)
                lp_bstr = pointer(bstr)
                admin.add_fraction_result(exp_id, i, lp_bstr)

            # Now retrieve the fraction results from the dataset
            for i, fraction_result in enumerate(self.fraction_results_json):
                result = admin.get_fraction_result(exp_id, i)

                self.assertEqual(result, fraction_result)

            # Used to generate test file for test TestGetFractionResults()
            # admin.save_experiment(exp_id, "TestAddFractionResults [fake fraction data] (from 30k polystyrene treos + rex)")
        except Exception:
            success = False

        self.assertTrue(success)

    def test_12_get_fraction_results(self):
        exp_file_path = KnownPaths().get_experiment_data(
            "TestAddFractionResults [fake fraction data] (from 30k polystyrene treos + rex).afe8"
        )
        exp_id = admin.open_experiment(exp_file_path)

        success = True

        try:
            # Get the fraction results from the dataset
            for i, fraction_result in enumerate(self.fraction_results_json):
                result = admin.get_fraction_result(exp_id, i)

                self.assertTrue(len(result) > 0)

                self.assertEqual(result, fraction_result)
        except Exception:
            success = False

        self.assertTrue(success)


class B_SdkApiUnitTests(unittest.TestCase):
    def __init__(self, method_name: str = "SdkApiUnitTests") -> None:
        super().__init__(method_name)

    def test_30_show(self):
        got_error = False
        try:
            admin.astra_com.Show(True)
            admin.astra_com.Show(False)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_31_get_experiment_templates(self):
        SdkHelper().restart_astra_and_wait()
        got_error = False
        templates = None
        try:
            templates = admin.astra_com.GetExperimentTemplates()
        except Exception:
            got_error = True
        
        self.assertLess(0, len(templates))
        self.assertFalse(got_error)

    def test_32_new_experiment_from_template(self):
        SdkHelper().restart_astra_and_wait()
        got_error = False
        templates = None
        try:
            templates = admin.astra_com.GetExperimentTemplates()
        except Exception:
            got_error = True
        
        self.assertLess(0, len(templates))

        try:
            exp_id = admin.astra_com.NewExperimentFromTemplate(templates[0])
        except Exception:
            got_error = True

        self.assertTrue(exp_id > 0)
        self.assertFalse(got_error)

    def test_33_save_experiment(self):
        SdkHelper().restart_astra_and_wait()
        got_error = False
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_file_path_saving = KnownPaths().get_experiment_data("test_33_save_experiment")
        try:  
            exp_id = admin.open_experiment(exp_file_path)
            admin.save_experiment(exp_id, exp_file_path_saving)
        except Exception:
            got_error = True

        self.assertTrue(os.path.exists(exp_file_path_saving + ".afe8"))
        self.assertFalse(got_error)

    def test_34_close_experiment(self):
        got_error = False
        try:
            exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
            exp_id = admin.open_experiment(exp_file_path)
            admin.close_experiment(exp_id)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_35_get_experiment_name(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            name = admin.astra_com.GetExperimentName(exp_id)
        except Exception:
            got_error = True

        self.assertTrue(len(name) > 0)
        self.assertFalse(got_error)

    def test_36_get_experiment_description(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.GetExperimentDescription(exp_id)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_37_set_experiment_description(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.astra_com.SetExperimentDescription(
                exp_id, "set_experiment_description"
            )
            result = admin.astra_com.GetExperimentDescription(exp_id)
        except Exception:
            got_error = True

        self.assertEqual("set_experiment_description", result)
        self.assertFalse(got_error)

    def test_38_get_collection_duration(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.get_collection_duration(exp_id)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_39_set_collection_duration(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.set_collection_duration(exp_id, 0.55)
            result = admin.get_collection_duration(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.55, result)
        self.assertFalse(got_error)

    def test_40_validate_experiment(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = True
        try:
            error, result = admin.astra_com.ValidateExperiment(exp_id)
        except Exception:
            got_error = True

        self.assertTrue(result)
        self.assertEqual(None, error)
        self.assertFalse(got_error)

    def test_41_use_instrument_calibration_constant(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.UseInstrumentCalibrationConstant(exp_id, True)
            admin.astra_com.UseInstrumentCalibrationConstant(exp_id, False)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_42_start_stop_collection(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.StartCollection(exp_id)
            admin.astra_com.StopCollection(exp_id)
        except Exception as ex:
            self.assertEqual('Could not view the Basic Collection Procedure.', ex.args[2][0])
            got_error = True

        self.assertTrue(got_error)
        got_error = False

        try:
            admin.astra_com.StopCollection(exp_id)
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_43_get_set_pump_flow_rate(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_pump_flow_rate(exp_id, 0.11)
            result = admin.get_pump_flow_rate(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_44_get_set_injected_volume(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_injected_volume(exp_id, 0.11)
            result = admin.get_injected_volume(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_45_get_set_sample(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            result: SampleInfo = admin.get_sample(exp_id)
            result.name = "test_get_set_sample"
            admin.set_sample(exp_id, result)
            result = admin.get_sample(exp_id)
        except Exception:
            got_error = True

        self.assertEqual("test_get_set_sample", result.name)
        self.assertFalse(got_error)

    def test_46_get_set_sample_name(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_name(exp_id, "test_get_set_sample_name")
            result = admin.get_sample_name(exp_id)
        except Exception:
            got_error = True

        self.assertEqual("test_get_set_sample_name", result)
        self.assertFalse(got_error)

    def test_47_get_set_sample_description(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_description(
                exp_id, "test_get_set_sample_description"
            )
            result = admin.get_sample_description(exp_id)
        except Exception:
            got_error = True

        self.assertEqual("test_get_set_sample_description", result)
        self.assertFalse(got_error)

    def test_48_get_set_sample_dndc(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_dndc(exp_id, 0.11)
            result = admin.get_sample_dndc(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_49_get_set_sample_a2(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_a2(exp_id, 0.11)
            result = admin.get_sample_a2(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_50_get_set_sample_uv_extinction(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_uv_extinction(exp_id, 0.11)
            result = admin.get_sample_uv_extinction(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_51_get_set_sample_concentration(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            admin.set_sample_concentration(exp_id, 0.11)
            result = admin.get_sample_concentration(exp_id)
        except Exception:
            got_error = True

        self.assertEqual(0.11, result)
        self.assertFalse(got_error)

    def test_52_instruments_detected(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.InstrumentsDetected
        except Exception:
            got_error = True

        self.assertEqual(1, result)
        self.assertFalse(got_error)

    def test_53_open_experiment(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)

        self.assertTrue(exp_id > 0)

    def test_54_get_results_snapshot(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetResultsSnapshot(exp_id)
        except Exception:
            got_error = True

        self.assertTrue(len(result) > 0)
        self.assertFalse(got_error)

    def test_55_get_is_experiment_running(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetIsExperimentRunning(exp_id)
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_56_get_automation_uid(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetAutomationUid()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_57_get_automation_client_info(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetAutomationClientInfo()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_58_get_automation_client_process_id(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetAutomationClientProcessId()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_59_validate_logon(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.ValidateLogon("userId", "password", "domain")
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_60_get_data_database_directory(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetDataDatabaseDirectory("")
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_61_has_vision_uv(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            result = admin.astra_com.HasVisionUv(exp_id)
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_62_setup_vision_uv(self):
        # experiment without vision uv
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            lp_details = pointer(AstraAdmin.UvDeviceDetails(
                deviceModel = comtypes.BSTR('test_62'),
                deviceName = comtypes.BSTR('test_62'),
                peakWidth = comtypes.BSTR('test_62'),
                slitWidth = comtypes.BSTR('test_62'),
            ))
            result = admin.astra_com.SetupVisionUv(
                exp_id,
                lp_details
            )
        except Exception as ex:
            got_error = True
            self.assertEqual("No VISION UV instrument was found in configuration.", ex.args[2][0])

        self.assertIsNone(result)
        self.assertTrue(got_error)

        # experiment with vision uv
        exp_file_path = KnownPaths().get_experiment_data("python uv tests.afe8")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            lp_details = pointer(AstraAdmin.UvDeviceDetails(
                deviceModel = comtypes.BSTR('test_62'),
                deviceName = comtypes.BSTR('test_62'),
                peakWidth = comtypes.BSTR('test_62'),
                slitWidth = comtypes.BSTR('test_62'),
            ))
            result = admin.astra_com.SetupVisionUv(
                exp_id,
                lp_details
            )
        except Exception as ex:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_63_push_vision_uv_data(self):
        # experiment without vision uv
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.PushVisionUvData(exp_id, 1, [0.1, 0.2])
        except Exception as ex:
            self.assertEqual("UV data does not match expected input.", ex.args[2][0])
            got_error = True

        self.assertTrue(got_error)

        # experiment with vision uv
        exp_file_path = KnownPaths().get_experiment_data("python uv tests.afe8")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.PushVisionUvData(exp_id, 1, [0.1, 0.2])
        except Exception as ex:
            got_error = True

        self.assertFalse(got_error)

    def test_64_save_experiment_with_description(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        try:
            admin.astra_com.SaveExperimentWithDescription(
                exp_id, KnownPaths().get_experiment_data("test_64_save_experiment_with_description.afe7"), "test_save_experiment_with_description"
            )
        except Exception:
            got_error = True

        self.assertFalse(got_error)

    def test_65_get_window_handle(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetWindowHandle()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_66_is_embedded(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.IsEmbedded()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_67_has_collected_data(self):
        exp_file_path = KnownPaths().get_experiment_data("30k polystyrene treos + rex.afe7")
        exp_id = admin.open_experiment(exp_file_path)
        got_error = False
        result = None
        try:
            result = admin.astra_com.HasCollectedData(exp_id)
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)

    def test_68_get_version(self):
        got_error = False
        result = None
        try:
            result = admin.astra_com.GetVersion()
        except Exception:
            got_error = True

        self.assertIsNotNone(result)
        self.assertFalse(got_error)


if __name__ == "__main__":
    unittest.main()
    AstraAdmin().dispose()
