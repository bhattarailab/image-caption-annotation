import os
import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QFileDialog, QTextEdit, QPushButton, QMessageBox, 
    QLineEdit, QSplitter, QFrame)
from PyQt5.QtGui import QPixmap, QIntValidator, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt

class TextAnnotationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Original text editor
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Original caption")
        
        # Buttons for marking text
        button_layout = QHBoxLayout()
        self.mark_correct_btn = QPushButton("Mark Correct")
        self.mark_incorrect_btn = QPushButton("Mark Incorrect")
        self.clear_marks_btn = QPushButton("Clear Marks")
        button_layout.addWidget(self.mark_correct_btn)
        button_layout.addWidget(self.mark_incorrect_btn)
        button_layout.addWidget(self.clear_marks_btn)
        
        # Correction editor
        self.correction_editor = QTextEdit()
        self.correction_editor.setPlaceholderText("Enter corrections for incorrect parts here")
        
        # Connect buttons
        self.mark_correct_btn.clicked.connect(lambda: self.mark_text('correct'))
        self.mark_incorrect_btn.clicked.connect(lambda: self.mark_text('incorrect'))
        self.clear_marks_btn.clicked.connect(self.clear_marks)
        
        # Add widgets to layout
        layout.addWidget(QLabel("Original Caption:"))
        layout.addWidget(self.text_editor)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Corrections:"))
        layout.addWidget(self.correction_editor)
        
        # Store annotations
        self.annotations = {}
        
    def mark_text(self, mark_type):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        if mark_type == 'correct':
            format.setBackground(QColor('#90EE90'))  # Light green
        else:
            format.setBackground(QColor('#FFB6C1'))  # Light red
            
        # Store the new annotation
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        selected_text = cursor.selectedText()

        # Check for overlapping annotations and remove them
        overlapping_keys = []
        for key, annotation in self.annotations.items():
            # Check if the new selection overlaps with existing annotation
            if not (end <= annotation['start'] or start >= annotation['end']):
                overlapping_keys.append(key)
        
        # Remove overlapping annotations
        for key in overlapping_keys:
            del self.annotations[key]
            
        # Add the new annotation
        self.annotations[f"{start}-{end}"] = {
            'text': selected_text,
            'type': mark_type,
            'start': start,
            'end': end
        }
        
        # Reapply all annotations to ensure proper visualization
        self.reapply_all_annotations()

    def reapply_all_annotations(self):
        # Store current cursor position
        current_cursor = self.text_editor.textCursor()
        current_position = current_cursor.position()
        
        # First clear all formatting
        document = self.text_editor.document()
        cursor = QTextCursor(document)
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        format.setBackground(QColor('white'))
        cursor.mergeCharFormat(format)
        
        # Sort annotations by start position
        sorted_annotations = sorted(
            self.annotations.values(), 
            key=lambda x: x['start']
        )
        
        # Reapply each annotation
        cursor = QTextCursor(document)
        for annotation in sorted_annotations:
            cursor.setPosition(annotation['start'])
            cursor.setPosition(annotation['end'], QTextCursor.KeepAnchor)
            
            format = QTextCharFormat()
            if annotation['type'] == 'correct':
                format.setBackground(QColor('#90EE90'))
            else:
                format.setBackground(QColor('#FFB6C1'))
                
            cursor.mergeCharFormat(format)
        
        # Restore cursor to previous position without selection
        current_cursor.setPosition(current_position)
        self.text_editor.setTextCursor(current_cursor)
        
        # Force update
        self.text_editor.viewport().update()

    def clear_marks(self):
        # Store current cursor position
        cursor = self.text_editor.textCursor()
        current_position = cursor.position()
        
        # Clear formatting
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        format.setBackground(QColor('white'))
        cursor.mergeCharFormat(format)
        
        # Restore cursor to previous position without selection
        cursor.setPosition(current_position)
        self.text_editor.setTextCursor(cursor)
        
        self.annotations = {}
        self.correction_editor.clear()
        
        # Force update
        self.text_editor.viewport().update()

    def get_annotations_data(self):
        return {
            'original_text': self.text_editor.toPlainText(),
            'corrections': self.correction_editor.toPlainText(),
            'annotations': self.annotations
        }

    def set_annotations_data(self, data):
        if not data:
            return
            
        # Clear marks without selecting all text
        self.clear_marks()
        
        # Set text without selecting it
        cursor = self.text_editor.textCursor()
        cursor.setPosition(0)
        self.text_editor.setTextCursor(cursor)
        
        self.text_editor.setPlainText(data.get('original_text', ''))
        self.correction_editor.setPlainText(data.get('corrections', ''))
        
        # Set annotations
        self.annotations = data.get('annotations', {})
        
        # Apply all annotations
        self.reapply_all_annotations()
        
        # Move cursor to start without selection
        cursor = self.text_editor.textCursor()
        cursor.setPosition(0)
        self.text_editor.setTextCursor(cursor)
        
        # Force update
        self.text_editor.viewport().update()

class LabelingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Labeling Software")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create a splitter for image and annotation
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Image and image name
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout(self.image_widget)
        
        # Add image name label
        self.image_name_label = QLabel()
        self.image_name_label.setAlignment(Qt.AlignCenter)
        self.image_name_label.setStyleSheet("font-weight: bold; padding: 5px;")
        self.image_layout.addWidget(self.image_name_label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)
        
        # Right side - Annotation
        self.annotation_widget = TextAnnotationWidget()
        
        # Add widgets to splitter
        self.splitter.addWidget(self.image_widget)
        self.splitter.addWidget(self.annotation_widget)
        
        # Navigation controls
        self.navigation_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.save_button = QPushButton("Save")
        self.image_number_input = QLineEdit()
        self.image_number_input.setPlaceholderText("Enter image number")
        self.image_number_input.setValidator(QIntValidator(1, 9999))
        self.go_button = QPushButton("Go")
        
        self.navigation_layout.addWidget(self.prev_button)
        self.navigation_layout.addWidget(self.next_button)
        self.navigation_layout.addWidget(self.save_button)
        self.navigation_layout.addWidget(self.image_number_input)
        self.navigation_layout.addWidget(self.go_button)
        
        self.image_count_label = QLabel()
        self.image_count_label.setAlignment(Qt.AlignCenter)
        
        # Add everything to main layout
        self.layout.addWidget(self.splitter)
        self.layout.addWidget(self.image_count_label)
        self.layout.addLayout(self.navigation_layout)
        
        # Connect buttons
        self.prev_button.clicked.connect(self.load_previous_image)
        self.next_button.clicked.connect(self.load_next_image)
        self.save_button.clicked.connect(self.save_captions)
        self.go_button.clicked.connect(self.go_to_image)
        
        # Initialize variables
        self.image_dir = None
        self.json_file = None
        self.changed_files = set()
        self.captions = {}
        self.load_data()
        self.image_names = list(self.captions.keys())
        self.current_index = self.get_starting_index()
        self.is_caption_modified = False
        
        self.annotation_widget.text_editor.textChanged.connect(self.on_caption_changed)
        self.annotation_widget.correction_editor.textChanged.connect(self.on_caption_changed)

    def load_data(self):
        self.image_dir = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        self.json_file = QFileDialog.getOpenFileName(self, "Select JSON File", filter="JSON Files (*.json)")[0]

        if self.image_dir and self.json_file:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                # Convert old format to new format if necessary
                self.captions = {
                    k: {'original_text': v, 'corrections': '', 'annotations': {}} 
                    if isinstance(v, str) else v 
                    for k, v in data.items()
                }
            self.image_names = list(self.captions.keys())
            if self.image_names:
                starting_index = self.get_starting_index()
                self.load_image(self.image_names[starting_index])
    
    def get_starting_index(self):
        last_modified_file = os.path.join(os.path.dirname(self.json_file), 'last_modified.txt')
        if os.path.exists(last_modified_file):
            with open(last_modified_file, 'r') as f:
                last_modified_image = f.read().strip()
            if last_modified_image in self.image_names:
                return self.image_names.index(last_modified_image)
        return 0

    def load_image(self, image_name):
        image_path = os.path.join(self.image_dir, image_name)
        if os.path.exists(image_path):
            # Update image name label
            self.image_name_label.setText(f"Image Name: {image_name}")
            
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            # Load annotations
            self.annotation_widget.set_annotations_data(self.captions[image_name])
            
            self.current_index = self.image_names.index(image_name)
            self.update_image_count_label()
            self.is_caption_modified = False

    def save_captions(self):
        if self.json_file:
            current_image_name = self.image_names[self.current_index]
            
            # Get current annotations
            current_data = self.annotation_widget.get_annotations_data()
            
            if current_data != self.captions[current_image_name]:
                self.changed_files.add(current_image_name)
            
            self.captions[current_image_name] = current_data
            
            # Save to JSON
            with open(self.json_file, 'w') as f:
                json.dump(self.captions, f, indent=4)
            
            # Save last modified
            last_modified_file = os.path.join(os.path.dirname(self.json_file), 'last_modified.txt')
            with open(last_modified_file, 'w') as f:
                f.write(current_image_name)
            
            self.is_caption_modified = False
            QMessageBox.information(self, "Success", "Annotations saved successfully!")

    def on_caption_changed(self):
        self.is_caption_modified = True

    def prompt_save_changes(self):
        reply = QMessageBox.question(self, 'Save Changes',
                                     'Do you want to save the changes?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.save_captions()

    def closeEvent(self, event):
        if self.is_caption_modified:
            self.prompt_save_changes()
        self.on_exit()
        event.accept()

    def on_exit(self):
        print("Files changed:", self.changed_files)
        print("Changes saved to:", self.json_file)
    
    def update_image_count_label(self):
        total_images = len(self.image_names)
        current_image = self.current_index + 1
        self.image_count_label.setText(f"Image {current_image} of {total_images}")

    def load_next_image(self):
        if self.is_caption_modified:
            self.prompt_save_changes()
        next_index = (self.current_index + 1) % len(self.image_names)
        self.load_image(self.image_names[next_index])

    def load_previous_image(self):
        if self.is_caption_modified:
            self.prompt_save_changes()
        prev_index = (self.current_index - 1) % len(self.image_names)
        self.load_image(self.image_names[prev_index])

    def go_to_image(self):
        if self.is_caption_modified:
            self.prompt_save_changes()
        try:
            image_number = int(self.image_number_input.text())
            if 1 <= image_number <= len(self.image_names):
                self.load_image(self.image_names[image_number - 1])
            else:
                QMessageBox.warning(self, "Invalid Image Number", "Please enter a valid image number.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelingWindow()
    window.show()
    sys.exit(app.exec_())
