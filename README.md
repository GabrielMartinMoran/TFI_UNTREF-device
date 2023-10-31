[![Python v3.8+](https://img.shields.io/badge/Python-v3.8%2B-blue)](https://www.python.org/downloads)
[![codecov](https://codecov.io/gh/GabrielMartinMoran/TFI_UNTREF-device/branch/master/graph/badge.svg?token=PRPQM7JVK4)](https://codecov.io/gh/GabrielMartinMoran/TFI_UNTREF-device)

# Trabajo Final Integrador - Ingeniería en Computación - UNTREF

## Prototipo de medidor de consumo eléctrico y de prendido / apagado de energía eléctrica en ambientes controlados

## Smart Plug (Device)

### Setting up the project

Micropython installation reference document: [ESP32 Micropython Web](https://micropython.org/download/esp32/)


1. Install python or configure a virtual environment in the computer.
2. Install python dependencies specified in `requirements.txt`:

```shell
pip install -r requirements.txt
```

### Running the code in the computer
1. Run the python script `run.py`. 

### Running the tests
1. Run the script `run_tests.sh`.

### Flashing the code to the ESP32
1. Connect the NodeMCU ESP32 to the computer.
2. Run the script `erase_flash.sh` (avoid if micropython is already installed in the ESP32).
3. Run the script `flash_micropython.sh`  (avoid if micropython is already installed in the ESP32).
4. Run the python script `upload_scripts.sh`.
5. Restart the ESP32.
6. For viewing the ESP32 logs, the script `serial_connect.sh` can be used.

### ESP32 Quickref

Here it is a document with the documentation of micropython for using it in the ESP32: [ESP32 Micropython Quickref](https://docs.micropython.org/en/latest/esp32/quickref.html)

![NodeMCU ESP32 Pinout](NodeMCU-ESP32.jpg)