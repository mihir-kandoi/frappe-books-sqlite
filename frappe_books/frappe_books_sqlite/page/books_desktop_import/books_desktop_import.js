frappe.pages["books-desktop-import"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Import Desktop Books"),
		single_column: true,
	});
	const root = $(wrapper).find(".layout-main-section");
	root.html(`
		<div class="books-import-shell">
			<section class="books-import-intro">
				<div class="books-import-icon">${frappe.utils.icon("database", "xl")}</div>
				<div><h2>${__("Bring your desktop company into Frappe")}</h2><p>${__("Upload the .books.db file. The importer validates it first, preserves submitted and cancelled documents, and skips records already present.")}</p></div>
			</section>
			<section class="books-import-card">
				<div class="books-import-drop"><h3>${__("Desktop database")}</h3><p>${__("Nothing is imported until you review the preview and confirm.")}</p><button class="btn btn-primary books-upload">${__("Choose database")}</button><div class="books-selected"></div></div>
				<div class="books-preview"></div>
			</section>
			<section class="books-import-note"><strong>${__("Before you start")}</strong><span>${__("Keep a backup of the desktop file. Import into a fresh site for the cleanest result. Native CSV import and export remain available through Frappe Data Import and Data Export.")}</span></section>
		</div>`);
	root.find(".books-upload").on("click", () => choose_database(root, page));
	page.add_inner_button(__("Data Import"), () => frappe.set_route("List", "Data Import"));
	page.add_inner_button(__("Data Export"), () => frappe.set_route("List", "Data Export"));
};

function choose_database(root, page) {
	new frappe.ui.FileUploader({
		allow_multiple: false,
		folder: "Home/Attachments",
		on_success: async (file) => {
			root.find(".books-selected").text(file.file_name || file.file_url);
			page.set_indicator(__("Validating"), "orange");
			const { message } = await frappe.call({
				method: "frappe_books.migration.desktop_sqlite.preview_database",
				args: { file_url: file.file_url },
				freeze: true,
				freeze_message: __("Checking desktop database…"),
			});
			page.set_indicator(__("Ready"), "green");
			render_preview(root, file.file_url, message, page);
		},
	});
}

function render_preview(root, file_url, preview, page) {
	const rows = Object.entries(preview.counts)
		.sort((a, b) => b[1] - a[1])
		.map(([name, count]) => `<tr><td>${frappe.utils.escape_html(name)}</td><td>${count}</td></tr>`)
		.join("");
	root.find(".books-preview").html(`
		<div class="books-preview-head"><div><p>${__("Validated database")}</p><h3>${frappe.utils.escape_html(preview.database)}</h3></div><strong>${preview.records} ${__("records")}</strong></div>
		<div class="books-preview-stats"><span><b>${preview.tables}</b>${__("tables")}</span><span><b>${preview.mapped_tables}</b>${__("mapped tables")}</span><span><b>${preview.single_values}</b>${__("settings")}</span></div>
		<div class="books-count-table"><table><thead><tr><th>${__("Desktop table")}</th><th>${__("Rows")}</th></tr></thead><tbody>${rows}</tbody></table></div>
		<button class="btn btn-primary books-start-import">${__("Import into this site")}</button>`);
	root.find(".books-start-import").on("click", () => {
		frappe.confirm(
			__("Import this database now? Existing records with the same name will be skipped."),
			() => run_import(root, file_url, page)
		);
	});
}

async function run_import(root, file_url, page) {
	const { message } = await frappe.call({
		method: "frappe_books.migration.desktop_sqlite.import_database_file",
		type: "POST",
		args: { file_url },
		freeze: true,
		freeze_message: __("Importing desktop books…"),
	});
	page.set_indicator(__("Imported"), "green");
	root.find(".books-preview").html(`
		<div class="books-import-result"><div>${frappe.utils.icon("circle-check", "xl")}</div><h3>${__("Import complete")}</h3><p>${message.inserted_total} ${__("documents inserted")}; ${message.skipped_total} ${__("existing documents skipped")}; ${message.single_values} ${__("settings imported")}.</p><button class="btn btn-primary books-open-dashboard">${__("Open dashboard")}</button></div>`);
	root.find(".books-open-dashboard").on("click", () => frappe.set_route("books-dashboard"));
}
