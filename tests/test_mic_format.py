import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKETCH = (ROOT / "esp32-birdnet-mic" / "esp32-birdnet-mic.ino").read_text(encoding="utf-8")
WEBUI_CPP = (ROOT / "esp32-birdnet-mic" / "WebUI.cpp").read_text(encoding="utf-8")
WEBUI_HTML = (ROOT / "esp32-birdnet-mic" / "webui" / "index.html").read_text(encoding="utf-8")
README = (ROOT / "esp32-birdnet-mic" / "README.md").read_text(encoding="utf-8")


class MicFormatContractTest(unittest.TestCase):
    def test_firmware_formats_and_safe_default(self):
        self.assertIn("MIC_FORMAT_PHILIPS = 0", SKETCH)
        self.assertIn("MIC_FORMAT_MSB = 1", SKETCH)
        self.assertIn("DEFAULT_MIC_FORMAT = MIC_FORMAT_PHILIPS", SKETCH)
        self.assertIn("I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG", SKETCH)
        self.assertIn("I2S_STD_MSB_SLOT_DEFAULT_CONFIG", SKETCH)

    def test_setting_is_validated_and_persisted(self):
        self.assertIn('getUChar("micFormat", DEFAULT_MIC_FORMAT)', SKETCH)
        self.assertIn('putUChar("micFormat", micFormat)', SKETCH)
        self.assertIn("if (!micFormatSupported(micFormat))", SKETCH)
        self.assertIn("if (!micFormatSupported(newFormat)) return false;", SKETCH)
        self.assertIn("micFormat = oldFormat;", SKETCH)

    def test_api_and_ui_contract(self):
        self.assertIn('"\\\"mic_format\\\":" + String(micFormat)', WEBUI_CPP)
        self.assertIn('key == "mic_format"', WEBUI_CPP)
        self.assertIn("v <= 2", WEBUI_CPP)
        self.assertIn('\"pdm_supported\\"', WEBUI_CPP)
        self.assertIn("id='sel_mic_format'", WEBUI_HTML)
        self.assertIn("Adafruit SPH0645", WEBUI_HTML)
        self.assertIn("cannot damage the microphone", WEBUI_HTML)

    def test_pdm_option(self):
        self.assertIn("MIC_FORMAT_PDM = 2", SKETCH)
        self.assertIn("#if SOC_I2S_SUPPORTS_PDM2PCM", SKETCH)
        self.assertIn("i2s_channel_init_pdm_rx_mode", SKETCH)
        self.assertIn("I2S_PDM_RX_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT", SKETCH)
        self.assertIn("PDM_SAMPLE_RATE = 48000", SKETCH)
        # PDM is fixed-rate: other rates are rejected, stored settings repaired.
        self.assertIn("micFormat == MIC_FORMAT_PDM && newRate != PDM_SAMPLE_RATE", SKETCH)
        self.assertIn("micFormat == MIC_FORMAT_PDM && currentSampleRate != PDM_SAMPLE_RATE", SKETCH)
        # 16-bit PDM samples are read without the I2S shift.
        self.assertIn("bytesRead / bytesPerSample", SKETCH)
        self.assertIn("id='opt_mic_pdm'", WEBUI_HTML)
        self.assertIn("j.pdm_supported!==true", WEBUI_HTML)
        # PDM mode locks rate/shift controls and drops shift advice.
        self.assertIn("function applyMicMode(j)", WEBUI_HTML)
        self.assertIn("then(j=>{ applyMicMode(j);", WEBUI_HTML)
        self.assertIn("lock(['in_rate','btn_rate_set']", WEBUI_HTML)
        self.assertIn("lock(['in_shift','btn_shift_set']", WEBUI_HTML)
        self.assertIn("clip_bad:'CLIPPING! Reduce Gain.'", WEBUI_HTML)
        self.assertIn("### PDM Microphones (XIAO ESP32-S3 only)", README)


if __name__ == "__main__":
    unittest.main()
