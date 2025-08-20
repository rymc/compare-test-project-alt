import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from datetime import datetime
from typing import Optional

from speech_recorder import SpeechRecorder

class SpeechRecorderUI:
    """GUI for the Speech Recorder application."""
    
    def __init__(self):
        """Initialize the UI."""
        self.root = tk.Tk()
        self.speech_recorder = SpeechRecorder()
        self.setup_ui()
        self.setup_callbacks()
        self.refresh_transcriptions()
        self.update_status()
        
        # Auto-refresh timer
        self.root.after(1000, self.periodic_update)
    
    def setup_ui(self):
        """Set up the user interface."""
        self.root.title("Speech-to-Text Recorder")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Control Panel
        self.setup_control_panel(main_frame)
        
        # Status Panel
        self.setup_status_panel(main_frame)
        
        # Search Panel
        self.setup_search_panel(main_frame)
        
        # Transcriptions Panel
        self.setup_transcriptions_panel(main_frame)
        
        # Statistics Panel
        self.setup_stats_panel(main_frame)
    
    def setup_control_panel(self, parent):
        """Set up the control panel."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Service control buttons
        self.start_button = ttk.Button(
            control_frame, 
            text="Start Service", 
            command=self.start_service,
            style="Green.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop Service", 
            command=self.stop_service,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Manual recording button
        self.record_button = ttk.Button(
            control_frame,
            text="Manual Record",
            command=self.toggle_manual_recording,
            state=tk.DISABLED
        )
        self.record_button.grid(row=0, column=2, padx=5)
        
        # Model selection
        ttk.Label(control_frame, text="Whisper Model:").grid(row=0, column=3, padx=(20, 5))
        self.model_var = tk.StringVar(value="base")
        self.model_combo = ttk.Combobox(
            control_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=10
        )
        self.model_combo.grid(row=0, column=4, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.change_model)
        
        # Refresh button
        ttk.Button(
            control_frame,
            text="Refresh",
            command=self.refresh_transcriptions
        ).grid(row=0, column=5, padx=(20, 0))
    
    def setup_status_panel(self, parent):
        """Set up the status panel."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Service stopped", foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.recording_label = ttk.Label(status_frame, text="Not recording", foreground="gray")
        self.recording_label.grid(row=0, column=1, padx=(20, 0), sticky=tk.W)
        
        self.shortcut_label = ttk.Label(status_frame, text="Shortcut: Cmd+R", foreground="blue")
        self.shortcut_label.grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
    
    def setup_search_panel(self, parent):
        """Set up the search panel."""
        search_frame = ttk.LabelFrame(parent, text="Search Transcriptions", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        ttk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search
        ).grid(row=0, column=2, padx=(5, 0))
    
    def setup_transcriptions_panel(self, parent):
        """Set up the transcriptions panel."""
        trans_frame = ttk.LabelFrame(parent, text="Transcriptions", padding="10")
        trans_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        trans_frame.columnconfigure(0, weight=1)
        trans_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(trans_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("timestamp", "duration", "confidence", "text"),
            show="headings",
            height=15
        )
        
        # Configure columns
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("duration", text="Duration (s)")
        self.tree.heading("confidence", text="Confidence")
        self.tree.heading("text", text="Text")
        
        self.tree.column("timestamp", width=150, minwidth=100)
        self.tree.column("duration", width=80, minwidth=60)
        self.tree.column("confidence", width=80, minwidth=60)
        self.tree.column("text", width=400, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Context menu
        self.tree.bind("<Button-2>", self.show_context_menu)  # Right click on macOS
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right click on Windows/Linux
        
        # Buttons frame
        buttons_frame = ttk.Frame(trans_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="View Full Text",
            command=self.view_full_text
        ).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Delete Selected",
            command=self.delete_selected
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Export All",
            command=self.export_transcriptions
        ).grid(row=0, column=2, padx=5)
    
    def setup_stats_panel(self, parent):
        """Set up the statistics panel."""
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(stats_frame, text="No statistics available")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
    
    def setup_callbacks(self):
        """Set up callbacks for the speech recorder."""
        self.speech_recorder.set_recording_callbacks(
            on_start=self.on_recording_start,
            on_stop=self.on_recording_stop,
            on_transcription_complete=self.on_transcription_complete
        )
    
    def start_service(self):
        """Start the speech recording service."""
        def start_thread():
            success = self.speech_recorder.start_service()
            self.root.after(0, lambda: self.on_service_started(success))
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_service(self):
        """Stop the speech recording service."""
        self.speech_recorder.stop_service()
        self.on_service_stopped()
    
    def toggle_manual_recording(self):
        """Toggle manual recording."""
        if self.speech_recorder.is_recording:
            self.speech_recorder.stop_recording()
        else:
            self.speech_recorder.start_recording()
    
    def change_model(self, event=None):
        """Change the Whisper model."""
        new_model = self.model_var.get()
        
        def change_thread():
            success = self.speech_recorder.change_whisper_model(new_model)
            self.root.after(0, lambda: self.on_model_changed(success, new_model))
        
        threading.Thread(target=change_thread, daemon=True).start()
    
    def on_service_started(self, success):
        """Handle service start completion."""
        if success:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            self.status_label.config(text="Service running", foreground="green")
        else:
            messagebox.showerror("Error", "Failed to start service. Check console for details.")
    
    def on_service_stopped(self):
        """Handle service stop."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED)
        self.status_label.config(text="Service stopped", foreground="red")
        self.recording_label.config(text="Not recording", foreground="gray")
    
    def on_model_changed(self, success, model_name):
        """Handle model change completion."""
        if not success:
            messagebox.showerror("Error", f"Failed to load model '{model_name}'")
    
    def on_recording_start(self):
        """Handle recording start."""
        self.root.after(0, lambda: self.recording_label.config(text="🔴 Recording...", foreground="red"))
        self.root.after(0, lambda: self.record_button.config(text="Stop Recording"))
    
    def on_recording_stop(self):
        """Handle recording stop."""
        self.root.after(0, lambda: self.recording_label.config(text="Processing...", foreground="orange"))
        self.root.after(0, lambda: self.record_button.config(text="Manual Record"))
    
    def on_transcription_complete(self, transcription_id, text):
        """Handle transcription completion."""
        self.root.after(0, self.refresh_transcriptions)
        self.root.after(0, lambda: self.recording_label.config(text="Not recording", foreground="gray"))
    
    def refresh_transcriptions(self):
        """Refresh the transcriptions list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get transcriptions (search or all)
        search_term = self.search_var.get().strip()
        if search_term:
            transcriptions = self.speech_recorder.search_transcriptions(search_term)
        else:
            transcriptions = self.speech_recorder.get_all_transcriptions()
        
        # Add to tree
        for trans in transcriptions:
            trans_id, text, timestamp, duration, audio_file, confidence = trans
            
            # Format values
            formatted_timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            formatted_duration = f"{duration:.1f}" if duration else "N/A"
            formatted_confidence = f"{confidence:.2f}" if confidence else "N/A"
            preview_text = text[:100] + "..." if len(text) > 100 else text
            
            self.tree.insert("", tk.END, values=(
                formatted_timestamp,
                formatted_duration,
                formatted_confidence,
                preview_text
            ), tags=(trans_id,))
        
        # Update statistics
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display."""
        stats = self.speech_recorder.get_stats()
        stats_text = (
            f"Total: {stats['total_transcriptions']} | "
            f"Duration: {stats['total_duration_seconds']:.1f}s | "
            f"Avg Confidence: {stats['average_confidence']:.2f}"
        )
        self.stats_label.config(text=stats_text)
    
    def update_status(self):
        """Update status display."""
        status = self.speech_recorder.get_recording_status()
        
        # Update shortcut label
        shortcut_text = f"Shortcut: {status['shortcut']}"
        self.shortcut_label.config(text=shortcut_text)
        
        # Update model display
        self.model_var.set(status['current_model'])
    
    def on_search_change(self, event=None):
        """Handle search text change."""
        # Debounce search
        if hasattr(self, '_search_timer'):
            self.root.after_cancel(self._search_timer)
        self._search_timer = self.root.after(500, self.refresh_transcriptions)
    
    def clear_search(self):
        """Clear search field."""
        self.search_var.set("")
        self.refresh_transcriptions()
    
    def view_full_text(self):
        """View full text of selected transcription."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transcription to view.")
            return
        
        item = self.tree.item(selection[0])
        trans_id = int(item['tags'][0])
        
        # Get full transcription
        transcription = self.speech_recorder.database.get_transcription_by_id(trans_id)
        if transcription:
            # Show in a new window
            self.show_text_window(f"Transcription #{trans_id}", transcription[1])
    
    def show_text_window(self, title, text):
        """Show text in a new window."""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x400")
        
        text_widget = tk.Text(window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
    
    def delete_selected(self):
        """Delete selected transcription."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transcription to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transcription?"):
            item = self.tree.item(selection[0])
            trans_id = int(item['tags'][0])
            
            if self.speech_recorder.delete_transcription(trans_id):
                self.refresh_transcriptions()
                messagebox.showinfo("Success", "Transcription deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete transcription.")
    
    def export_transcriptions(self):
        """Export all transcriptions to a text file."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                transcriptions = self.speech_recorder.get_all_transcriptions()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Speech-to-Text Transcriptions Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for trans in transcriptions:
                        trans_id, text, timestamp, duration, audio_file, confidence = trans
                        f.write(f"ID: {trans_id}\n")
                        f.write(f"Timestamp: {timestamp}\n")
                        f.write(f"Duration: {duration}s\n")
                        f.write(f"Confidence: {confidence}\n")
                        f.write(f"Text: {text}\n")
                        f.write("-" * 30 + "\n\n")
                
                messagebox.showinfo("Success", f"Transcriptions exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export transcriptions: {e}")
    
    def show_context_menu(self, event):
        """Show context menu for transcription items."""
        # TODO: Implement context menu
        pass
    
    def periodic_update(self):
        """Periodic update of UI elements."""
        # Update recording status
        if hasattr(self.speech_recorder, 'is_recording'):
            if self.speech_recorder.is_recording and not self.recording_label.cget("text").startswith("🔴"):
                self.recording_label.config(text="🔴 Recording...", foreground="red")
        
        # Schedule next update
        self.root.after(1000, self.periodic_update)
    
    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            if self.speech_recorder.is_service_running():
                self.speech_recorder.stop_service()

def main():
    """Main entry point for the UI."""
    app = SpeechRecorderUI()
    app.run()

if __name__ == "__main__":
    main()
