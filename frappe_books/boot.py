"""Adjust the Apps page metadata contributed by installed applications."""


def boot_session(bootinfo):
	"""Keep Framework ahead of every installed application on the Apps page."""
	app_data = bootinfo.get("app_data") or []
	framework_app = next((app for app in app_data if app.get("app_name") == "frappe"), None)
	if not framework_app:
		return

	sequence_ids = []
	for app in app_data:
		sequence_id = app.get("sequence_id")
		if isinstance(sequence_id, (int, float)):
			sequence_ids.append(sequence_id)

	framework_app["sequence_id"] = min(sequence_ids, default=0) - 1
