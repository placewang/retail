ls /sys/class/tty/ttyUSB* -l

udevadm info /dev/ttyUSB*

sudo nano /etc/udev/rules.d/99-com.rules
  UBSYSTEM=="tty", ENV{ID_PATH}=="platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0", SYMLINK+="USB0"
	


