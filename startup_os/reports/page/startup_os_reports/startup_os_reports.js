frappe.pages['startup-os-reports'].on_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: '📊 StartupOS Reports',
		single_column: true
	});

	page.set_indicator('Ready', 'green');

	$(wrapper).find('.page-content').html(`
		<div class="sos-reports-container">
			<div class="sos-company-bar">
				<label class="sos-label">Company</label>
				<select id="sos-company" class="form-control sos-select"></select>
			</div>

			<div class="sos-grid">
				<div class="sos-card">
					<div class="sos-icon">📊</div>
					<h3>Investor Summary</h3>
					<p>Compliance score, financial highlights, cap table, and fundraising pipeline — all in one PDF.</p>
					<button class="btn btn-primary sos-btn" data-report="generate_investor_report" data-label="Investor_Summary">
						⬇ Download PDF
					</button>
					<div class="sos-status" id="status-investor"></div>
				</div>

				<div class="sos-card">
					<div class="sos-icon">📋</div>
					<h3>Cap Table Report</h3>
					<p>Full ownership breakdown, transaction history, and ESOP grants per shareholder.</p>
					<button class="btn btn-primary sos-btn" data-report="generate_cap_table_report" data-label="Cap_Table">
						⬇ Download PDF
					</button>
					<div class="sos-status" id="status-captable"></div>
				</div>

				<div class="sos-card">
					<div class="sos-icon">🇮🇳</div>
					<h3>DPIIT Compliance Report</h3>
					<p>DPIIT recognition status, incorporation checklist, compliance score, and all ROC filings.</p>
					<button class="btn btn-primary sos-btn" data-report="generate_dpiit_report" data-label="DPIIT_Report">
						⬇ Download PDF
					</button>
					<div class="sos-status" id="status-dpiit"></div>
				</div>

				<div class="sos-card">
					<div class="sos-icon">💸</div>
					<h3>Financial Projections</h3>
					<p>Pitch-ready 24-month projections with 3-scenario runway analysis.</p>
					<button class="btn btn-primary sos-btn" data-report="generate_financial_projections" data-label="Financial_Projections">
						⬇ Download PDF
					</button>
					<div class="sos-status" id="status-financial"></div>
				</div>

				<div class="sos-card sos-wide">
					<div class="sos-icon">📥</div>
					<h3>Audit-Ready Equity &amp; Compliance Export</h3>
					<p>3-sheet XLSX: all equity transactions, compliance events log, and cap table summary — ready for auditors, CA, or CS.</p>
					<button class="btn btn-success sos-btn" data-report="export_equity_audit" data-label="Equity_Audit" data-format="xlsx">
						⬇ Download XLSX
					</button>
					<div class="sos-status" id="status-audit"></div>
				</div>
			</div>
		</div>

		<style>
			.sos-reports-container { max-width: 900px; margin: 24px auto; padding: 0 16px; }
			.sos-company-bar { display: flex; align-items: center; gap: 12px; background: #fff; padding: 14px 20px; border-radius: 10px; border: 1px solid #e8ecf0; margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
			.sos-label { font-weight: 600; color: #1e3a5f; white-space: nowrap; font-size: 14px; margin-bottom: 0; }
			.sos-select { flex: 1; max-width: 400px; }
			.sos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
			.sos-card { background: #fff; border-radius: 12px; padding: 22px; border: 1px solid #e8ecf0; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: box-shadow 0.15s, transform 0.15s; }
			.sos-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.10); transform: translateY(-1px); }
			.sos-wide { grid-column: span 2; border-left: 4px solid #2d6a4f; }
			.sos-icon { font-size: 30px; margin-bottom: 10px; }
			.sos-card h3 { font-size: 15px; color: #1e3a5f; margin: 0 0 8px; font-weight: 700; }
			.sos-card p { font-size: 12.5px; color: #6c757d; margin: 0 0 16px; line-height: 1.6; }
			.sos-btn { font-size: 12.5px; font-weight: 600; }
			.sos-status { font-size: 12px; margin-top: 8px; min-height: 18px; }
			.sos-status.loading { color: #0d6efd; }
			.sos-status.success { color: #198754; }
			.sos-status.error { color: #dc3545; }
		</style>
	`);

	// Load companies
	frappe.call({
		method: 'frappe.client.get_list',
		args: { doctype: 'Company', fields: ['name'], limit: 50 },
		callback: function(r) {
			var $sel = $('#sos-company');
			$sel.empty();
			if (r.message && r.message.length) {
				r.message.forEach(function(c) {
					$sel.append('<option value="' + c.name + '">' + c.name + '</option>');
				});
			} else {
				$sel.append('<option value="">No companies found</option>');
			}
		}
	});

	// Report button clicks
	$(wrapper).on('click', '.sos-btn', function() {
		var $btn = $(this);
		var report = $btn.data('report');
		var label = $btn.data('label');
		var format = $btn.data('format') || 'pdf';
		var company = $('#sos-company').val();

		if (!company) {
			frappe.msgprint('Please select a company first.');
			return;
		}

		var statusMap = {
			'generate_investor_report': '#status-investor',
			'generate_cap_table_report': '#status-captable',
			'generate_dpiit_report':     '#status-dpiit',
			'generate_financial_projections': '#status-financial',
			'export_equity_audit':       '#status-audit'
		};
		var $status = $(statusMap[report] || '');
		$status.removeClass().addClass('sos-status loading').text('⏳ Generating ' + label + '...');
		$btn.prop('disabled', true);

		frappe.call({
			method: 'startup_os.reports.pdf_generator.' + report,
			args: { company: company },
			callback: function(r) {
				$btn.prop('disabled', false);
				if (r.message && r.message.filecontent) {
					var byteStr = atob(r.message.filecontent);
					var bytes = new Uint8Array(byteStr.length);
					for (var i = 0; i < byteStr.length; i++) {
						bytes[i] = byteStr.charCodeAt(i);
					}
					var mimeTypes = {
						'pdf': 'application/pdf',
						'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
						'html': 'text/html'
					};
					var blob = new Blob([bytes], { type: mimeTypes[r.message.type] || 'application/pdf' });
					var url = URL.createObjectURL(blob);
					var a = document.createElement('a');
					a.href = url;
					a.download = r.message.filename;
					document.body.appendChild(a);
					a.click();
					document.body.removeChild(a);
					URL.revokeObjectURL(url);
					$status.removeClass().addClass('sos-status success').text('✅ ' + r.message.filename + ' downloaded!');
				} else {
					$status.removeClass().addClass('sos-status error').text('❌ Generation failed. Check server logs.');
				}
			},
			error: function() {
				$btn.prop('disabled', false);
				$status.removeClass().addClass('sos-status error').text('❌ API error. Is weasyprint/openpyxl installed?');
			}
		});
	});
};
