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
	@echo "Creating messy directory structure..."
	@mkdir -p example/messy/{"01_stuff/IMPORTANT docs","Downloads/pictures","My Documents/FINAL","notes","random_stuff123/old","temp/Temporary Files"}
	@echo "just some random notes\nTODO: organize this later\nremember to check this\nIMPORTANT!!! don't forget about the meeting" > "example/messy/01_stuff/random.txt"
	@echo "VERY IMPORTANT DOCUMENT\nDO NOT DELETE\nLast updated: 2023-12-01\n\nThis document contains critical information that needs to be organized better." > "example/messy/01_stuff/IMPORTANT docs/doc1.PDF"
	@echo "Draft version 1\nNeed to review this\nStatus: In Progress\nAuthor: John\nDate: 2023-11-15" > "example/messy/My Documents/FINAL/final_v1.doc"
	@echo "# TODOs\n\n- [ ] organize files\n- [x] backup important stuff\n* clean up downloads folder\n- URGENT: review documents\n* maybe delete old files?\n\n## Random Notes\n- check this later\n- important meeting on Friday" > "example/messy/notes/todo.md"
	@touch "example/messy/Downloads/img1.PNG" \
		"example/messy/Downloads/IMG2.png" \
		"example/messy/Downloads/pictures/screenshot 2024.png" \
		"example/messy/01_stuff/IMPORTANT docs/Doc2.pdf" \
		"example/messy/My Documents/FINAL/FINAL_V2.DOC" \
		"example/messy/My Documents/FINAL/final_FINAL_v3.docx" \
		"example/messy/My Documents/draft.TXT" \
		"example/messy/notes/TODOs.MD" \
		"example/messy/random_stuff123/backup.bak" \
		"example/messy/random_stuff123/old/archive.zip" \
		"example/messy/temp/temp.tmp" \
		"example/messy/temp/Temporary Files/delete_me.txt"
	@echo "✨ Messy directory structure created successfully!"

example-clean:
	@echo "Cleaning up messy directory..."
	@rm -rf example/messy
	@echo "🧹 Messy directory cleaned up successfully!" 