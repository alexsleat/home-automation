# Rename example_settings.py to settings.py and input your details.

mkdir /home/pi/logs

sudo crontab -e:

# Add the line:
@reboot sh /home/pi/home-automation/dash/launcher.sh >/home/pi/logs/cronlog 2>&1

# Reboot
