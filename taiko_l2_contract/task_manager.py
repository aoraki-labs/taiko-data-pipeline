from .block_scanner import BlockScanner


class TaskManager:
    def __init__(self):
        self.scanner = BlockScanner()

    def run(self):
        self.scanner.get_all_contracts_info()
        self.scanner.save_all_contracts_info()
    

if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.run()