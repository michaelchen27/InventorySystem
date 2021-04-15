# **Embedded Inventory System**

Embedded System Design

Jovan, Michael, Ryukin, William

## **Introduction**

Dalam menjalankan kegiatan peminjaman barang pada lab FTI, mahasiswa seringkali mengalami kesulitan untuk melakukan peminjaman barang dikarenakan metode manual yang masih dilakukan, yaitu menggunakan kertas dan alat tulis. Pendataan data peminjaman juga susah dilakukan, seperti pada aspek pelacakan terhadap barang yang sedang dipinjam atau telah dikembalikan, kapan barang tersebut dipinjam, dan oleh siapa barang tersebut dipinjam.

Berdasarkan masalah tersebut, penulis dari grup 1 mengusulkan pembuatan proses pendataan barang secara automasi dengan menggunakan teknologi sistem tertanam. Sistem yang diusulkan akan dibuat dengan menggunakan Raspberry Pi Zero sebagai CPU dengan menggunakan RC522 RFID module untuk memberikan label pada barang dan membaca barang sewaktu seorang mahasiswa ingin meminjam barang tersebut dan juga untuk membaca kartu mahasiswa untuk mendata data sang peminjam barang. Sistem tersebut diharapkan mampu merekam seluruh transaksi pinjam meminjam yang terjadi.

## **List of Components**

**Raspberry Pi Zero W**

- Komputer mini yang sudah terpasang WiFi module sehingga memperbolehkan akses tanpa monitor menggunakan SSH dan juga akses ke internet.
- Menjalankan OS Raspbian dengan environment Python yang telah terpasang dari awal sehingga mempermudah pemrograman bahasa Python.
- Harga yang murah dengan ukuran relatif kecil membuat ukuran perangkat kecil dan ringan.

**RC522 RFID Reader Module**

- Reader RFID dengan harga yang relatif murah. Supply voltage kecil yang berkisar di 2.5 ~ 3.3V dengan jarak baca ±5 cm. Voltage 5 volt dapat digunakan untuk logic input. Membaca di rentang frekuensi 13.56 MHz (HF).
- Paling umum dan paling banyak digunakan untuk project sederhana.

**EL-MF1-T1 RFID Tag**

- Tag berbentuk keychain yang dapat dikaitkan kepada benda ataupun ditempel menggunakan double-sided tape.
- Bekerja di frekuensi yang sama dengan reader sehingga compatible.

**MF1ICS50 RFID Card**

- Tag RFID berbentuk kartu digunakan untuk mensimulasikan kartu KTM mahasiswa dikarenakan KTM mahasiswa dienkripsi.
- Komponen ini tidak wajib karena dapat digantikan dengan RFID Tag berbentuk keychain.

**General Desktop Monitor**

- Monitor yang memiliki port HDMI untuk menampilkan update pada Google Sheets.
- Menu juga akan ditampilkan kepada user melalui monitor.

**Raspberry Pi Power Adapter**

- Raspberry Pi Zero W akan diberi supply melalui soket yang terhubung di tembok. Oleh karena itu diperlukan adapter yang dapat mengeluarkan output sekitar 5V 3A.

**HDMI to Mini HDMI Converter**

- Port HDMI Raspberry Pi Zero W berjenis mini HDMI sehingga diperlukan converter.

**Perfboard**

- Papan yang akan menjadi dasar komponen ditempelkan/ disolder. Digunakan perfboard karena penggunaannya yang relatif mudah dan cepat.

**LED Lights**

- Memberikan feedback berupa cahaya yang dapat dilihat oleh user.

**Buzzer**

- Memberikan feedback berupa suara yang dapat didengar oleh user.

## **Hardware Schematic Diagram**

![](https://github.com/michaelchen27/InventorySystem/blob/master/photos/Hardware%20Schematic.jpg)

- **Pin Raspberry Pi**

![](https://github.com/michaelchen27/InventorySystem/blob/master/photos/Pin.jpg)
  - SDA connects to Pin 24.

  - SCK connects to Pin 23.

  - MOSI connects to Pin 19.

  - MISO connects to Pin 21.

  - GND connects to Pin 6.

  - RST connects to Pin 22.

  - 3.3v connects to Pin 1.

  - LED\_VCC connects to Pin 12.

  - LED\_Ground connects to Pin 14.

- **Raspberry Pi dengan RFID Reader**
  - GPIO, dengan SPI Protocol
  - Memberi tegangan 3.3V pada RFID Reader
- **Raspberry Pi dengan LED**
  - GPIO
- **Raspberry Pi dengan PC**
  - Micro USB to USB
- **Raspberry Pi dengan Buzzer**
  - GPIO
  - Terhubung dengan Resistor 200 Ohm

## **Software Module**

Software module tanpa menggunakan module tkinter sebagai display module adalah sebagai berikut:

![](https://github.com/michaelchen27/InventorySystem/blob/master/photos/Software%20Module.jpg)

Secara garis besar, sistem bekerja berdasarkan modul:

- **Reservation dan Returning Module**

Reservation dan Returning module menggunakan data yang didapat RFID Reader untuk melakukan reservasi barang dan pengembalian barang. RFID Reader berupa contended-child, dan akses untuk module tersebut diatur oleh MAIN module, Reservation dan Returning module tidak akan dijalankan bersamaan.

- **RFID Reader Module**

Raspberry Pi menggunakan library SimpleMFRC522 untuk berkomunikasi dengan RFID Reader. Library ini menyediakan fungsi untuk berkomunikasi dengan RFID Reader dan menyediakan implementasi metode komunikasi yang digunakan, yaitu SPI protocol. Fungsi yang relevan untuk sistem ini berupa fungsi read RFID tag dan fungsi write RFID tag.

- **Database (gspread library)**

Module yang mengatur interaksi sistem dengan database. Google Sheets digunakan sebagai database untuk menyimpan data barang dan data peminjaman. Sistem berkomunikasi dengan Google Sheets API menggunakan gspread library. gspread menyediakan fungsi untuk autentikasi sehingga Raspberry Pi dapat memodifikasi isi dari sheets. Library ini berkomunikasi dengan melalui internet. Implementasi konektivitas ke internet diatur oleh Raspbian OS dan hanya digunakan melalui database module.

- **LED Module**

LED digunakan hanya untuk memberi notifikasi ke user bahwa proses pembacaan RFID tag sukses. Komunikasi hanya menggunakan GPIO

- **Display Module**

Implementasi display diatur oleh Raspbian OS dan built-in library dalam python (i.e., print function). Bentuk display yang diterapkan sekarang hanya berupa console melalui SSH. Rencana penerapan display module berupa menampilkan GUI yang dapat berinteraksi dengan user dan ditampilkan pada suatu monitor.

Berikut adalah software module diagram dengan menggunakan tkinter sebagai Display Module (Graphic User Interface (GUI)) 

![](https://github.com/michaelchen27/InventorySystem/blob/master/photos/Software%20Module.jpg)

- Module tkinter berupa blocking GUI, CPU thread Raspberry Pi tidak dapat menjalankan proses lain ketika menampilkan GUI tersebut.
  - Tkinter berupa event-based programming, maka tkinter module akan block semua proses pada thread sampai suatu event terjadi
- RFID reader library juga berupa proses blocking, maka diterapkan multithreading untuk mengatasi dua proses blocking
  - Tkinter module berupa thread utama yang dijalankan oleh Raspberry Pi
  - Ketika peminjaman atau pengembalian terjadi (event), tkinter module akan menjalankan proses RFID reader pada thread lain, dan menunggu hasil dari thread tersebut
  - Ketika RFID reader berhasil membaca dan mengembalikan hasil bacaan, tkinter module akan memproses hasil bacaan berdasarkan peminjaman atau pengembalian

## **Software Relation Diagram**

![](https://github.com/michaelchen27/InventorySystem/blob/master/photos/Software%20Relation.jpg)

- RFID Reader berkomunikasi dengan Raspberry Pi Zero W dengan protokol komunikasi SPI.
- RFID Driver yang digunakan adalah SimpleMFRC522 dalam bahasa pemrograman Python, berjalan di dalam Raspberry Pi.
- Data yang diterima akan diunggah ke internet menggunakan library gspread. WiFi Module dapat melakukan Wireless Connection ke Router terdekat.
- OS Raspberry Pi yang memiliki GUI akan ditampilkan kepada user melalui Monitor yang terhubung menggunakan HDMI. Dalam tampilan tersebut akan terdapat tampilan file Google Spreadsheet yang terhubung dengan Raspberry Pi.
- Sumber tegangan Raspberry Pi didapat dari power socket di tembok melalui adapter dan kabel micro USB.
- Menyimpan data sementara dari database pada temporary data.
