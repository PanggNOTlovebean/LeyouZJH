import tkinter as tk
from multiprocessing import Process, Queue
import time

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multiprocess GUI Application")
        self.geometry("400x300")
        self.process_counter = 0
        self.queues = []
        self.text_boxes = []

        self.start_process_button = tk.Button(self, text="Start New Process", command=self.start_new_process)
        self.start_process_button.pack(pady=10)

        self.after(100, self.check_queues)
         # 添加按钮
        self.add_button = tk.Button(self, text="Add Text Box", command=self.add_text_box)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(self, text="Remove Last Text Box", command=self.remove_text_box)
        self.remove_button.pack(pady=5)
        

    def start_new_process(self):
        queue = Queue()
        self.queues.append(queue)

        text_box = tk.Text(self, height=3, width=30)
        text_box.pack(pady=5)
        self.text_boxes.append(text_box)

        
        
       
        
        process = Process(target=self.process_task, args=(self.process_counter, queue))
        process.start()
        self.process_counter += 1
        
    def add_text_box(self):
        text_box = tk.Text(self, height=3, width=30, state=tk.DISABLED)
        text_box.pack(pady=5)
        self.text_boxes.append(text_box)

    def remove_text_box(self):
        if self.text_boxes:
            text_box = self.text_boxes.pop()
            text_box.destroy()
            
    def check_queues(self):
        for i, queue in enumerate(self.queues):
            if not queue.empty():
                message = queue.get()
                self.text_boxes[i].insert(tk.END, message)
        self.after(100, self.check_queues)

    def process_task(self, process_id, queue):
        for i in range(1, 11):
            time.sleep(1)
            message = f"Process {process_id}: {i}\n"
            queue.put(message)

app = Application()
app.mainloop()