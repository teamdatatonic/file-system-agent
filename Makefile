# Makefile for managing this FileSystemAgent project

# 1) Install: Set up dependencies with Poetry
install:
	poetry install

# 2) Test: Run pytest
test:
	poetry run pytest tests.py

# 3) Start: Launch the FileSystemAgent
start:
	poetry run python agent.py

# 4) Clean: Remove temporary files, caches, etc.
clean:
	rm -rf __pycache__ .pytest_cache coverage* *.egg-info
	find . -name "*.pyc" -delete
	rm -rf .venv
	rm -f poetry.lock

# 5) Example: Create a messy directory structure
example-build:
	@echo "Creating messy insurance company directory structure..."
	@mkdir -p "example/messy/Client_Files/Active_Claims" \
		"example/messy/Client_Files/Archived (2023)" \
		"example/messy/Forms & Templates/Policy_Forms" \
		"example/messy/Forms & Templates/Claims Forms" \
		"example/messy/Internal Documents/Meeting Notes" \
		"example/messy/Internal Documents/Procedures" \
		"example/messy/Scanned Documents/Pending Review" \
		"example/messy/Email Attachments/To Process" \
		"example/messy/Reports/Monthly/2024" \
		"example/messy/Training Materials/New Employee"
	
	@echo "CLAIM FORM - AUTO ACCIDENT\nDate: 2024-01-15\nClaim #: AC-2024-0123\nStatus: Pending Review\nClient: John Smith\nPolicy #: POL-789-012" > "example/messy/Client_Files/Active_Claims/Smith_J_Claim_2024-01.pdf"
	@echo "Meeting Minutes - Claims Review\nDate: 2024-02-01\nAttendees: Sarah, Mike, Jennifer\nAction Items:\n- Follow up on Smith claim\n- Update policy templates\n- Schedule client interviews" > "example/messy/Internal Documents/Meeting Notes/claims_review_feb2024.docx"
	@echo "Standard Operating Procedure\nLast Updated: 2023-12-15\nDepartment: Claims Processing\nVersion: 2.3\n\nPROCEDURE STEPS:\n1. Verify policy status\n2. Review claim documentation\n3. Assess coverage eligibility" > "example/messy/Internal Documents/Procedures/Claims_Processing_SOP_v2.3.doc"
	@echo "TO: claims@insurance.com\nFROM: client@email.com\nSUBJECT: Additional Documentation\n\nPlease find attached the requested medical records and repair estimates." > "example/messy/Email Attachments/To Process/FW_Additional_Docs_Smith_Case.eml"
	@echo "Monthly Claims Summary\nPeriod: January 2024\n\nTotal Claims: 45\nApproved: 32\nPending: 8\nDenied: 5\n\nTotal Payout: $123,456.78" > "example/messy/Reports/Monthly/2024/January_Claims_Summary_DRAFT.xlsx"

	@touch \
		"example/messy/Forms & Templates/Policy_Forms/Auto_Insurance_Application_2024.pdf" \
		"example/messy/Forms & Templates/Policy_Forms/Home_Insurance_Application_2024.pdf" \
		"example/messy/Forms & Templates/Claims Forms/Medical_Claim_Form_v3.pdf" \
		"example/messy/Forms & Templates/Claims Forms/Property_Damage_Form_2024.pdf" \
		"example/messy/Client_Files/Active_Claims/URGENT_Johnson_Medical_Claim.pdf" \
		"example/messy/Client_Files/Active_Claims/Williams_Property_Photos.zip" \
		"example/messy/Client_Files/Archived (2023)/Brown_Claim_Settled.pdf" \
		"example/messy/Scanned Documents/Pending Review/Medical_Records_Smith.pdf" \
		"example/messy/Scanned Documents/Pending Review/Repair_Estimate_Johnson.pdf" \
		"example/messy/Internal Documents/Meeting Notes/team_meeting_notes_old.doc" \
		"example/messy/Internal Documents/Meeting Notes/quarterly_review_2023Q4.pptx" \
		"example/messy/Training Materials/New Employee/onboarding_checklist.pdf" \
		"example/messy/Training Materials/New Employee/claims_processing_guide.pdf" \
		"example/messy/Email Attachments/To Process/Client_Statement_Brown.doc" \
		"example/messy/Reports/Monthly/2024/Claims_Analysis_JAN24_v2_FINAL.xlsx"

	@echo "✨ Insurance company directory structure created successfully!"

example-clean:
	@echo "Cleaning up messy directory..."
	@rm -rf example/messy
	@echo "🧹 Messy directory cleaned up successfully!" 