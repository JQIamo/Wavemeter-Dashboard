TARGET_UI_FILES: wavemeter_dashboard/view/ui/ui_dialog.py \
    wavemeter_dashboard/view/ui/ui_dashboard.py \
    wavemeter_dashboard/view/ui/ui_channel_setup.py \
    wavemeter_dashboard/view/ui/ui_channel_name_widget.py \
    wavemeter_dashboard/view/ui/ui_single_channel_display.py \
    wavemeter_dashboard/view/ui/ui_data_select.py



%.py: %.ui
	pyuic5 $< -o $@

.PHNOY: all clean

clean:
	rm $(TARGET_UI_FILES)

all: $(TARGET_UI_FILES)
