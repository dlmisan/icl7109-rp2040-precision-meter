# 📘 Usage Guide

This project uses a MicroPython-capable RP2040 board (e.g. Raspberry Pi Pico) to measure high-precision analog voltage and current using the ICL7109 ADC and display the results on a 128x64 I2C OLED.

---

## 🧰 Hardware Requirements

| Component    | Description                                |
| ------------ | ----------------------------------------   |
| RP2040 board | Raspberry Pi Pico (MicroPython firmware)   |
| ICL7109      | 0.01V 12-bit bipolar ADC (parallel output) |
| MC14052      | Analog multiplexer                         |
| SSD1306 OLED | 128x64 I2C display (address: `0x3D`)       |
| Button       | Used for mode switching (GPIO3)            |
| LED          | Indicates mode status (GPIO2)              |
| Resistors    | Pull-ups and voltage dividers as needed    |

---

## 🪛 Pin Connections (RP2040)

| Function            | GPIO  | Description                 |
| ------------------- | ----- | --------------------------- |
| OLED SDA            | 12    | I2C0 SDA                    |
| OLED SCL            | 13    | I2C0 SCL                    |
| ICL7109 STATUS      | 14    | Low when data is ready      |
| ICL7109 POL         | 15    | 1 = positive, 0 = negative  |
| ICL7109 OR          | 16    | Over-range detection        |
| MC14052 A/B         | 10/11 | Channel select pins (Y0–Y3) |
| Button Input        | 3     | Mode toggle, low-active     |
| Status LED          | 2     | Manual mode indicator       |
| ICL7109 Data B1–B12 | 17–28 | ADC data bits (LSB to MSB)  |

---

## ▶️ Getting Started

1. **Flash MicroPython firmware**
   Download and install the [MicroPython firmware](https://micropython.org/download/rp2-pico/) for Raspberry Pi Pico.

2. **Upload source files**
   Use [Thonny IDE](https://thonny.org/) or `mpremote` to upload the following files:

   * `main.py`
   * `writer.py`
   * `font/font10.py`

3. **Connect the hardware**
   Follow the GPIO mapping shown above.

4. **Power on the device**
   OLED will display:

   * Top: current mode (`AUTO`, `Y2`, `Y3`)
   * Middle: measured voltage
   * Bottom: measured current (in AUTO mode only)

5. **Press the button to switch modes**
   The display cycles through:

   * AUTO → Y2 → Y3 → AUTO

---

## 🖥️ OLED Display Layout

```
+-------------------------------+
|         [   AUTO   ]         |
|                               |
|         +1.234 V              |
|         +56.78 mA             |
+-------------------------------+
```

* In **AUTO** mode: voltage and current are alternately measured and both shown.
* In **Y2** mode: displays external voltage.
* In **Y3** mode: displays raw ADC value.

---

## 📌 Notes

* Voltage input should stay within ±0.01V.
* The project uses manual white background + black text for better visibility.
* You can extend this to add WiFi (e.g. Pico W), SD logging, or graphical plots.

---

For more details, see `README.md`. Contributions welcome!
