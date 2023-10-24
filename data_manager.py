import json
from datetime import datetime

class LogEntry:
    def __init__(self, ign, event_type, party_members, is_party_paused, timestamp=None):
        """
        Initialize a log entry.

        Args:
            ign (str): In-Game Name of the player.
            event_type (str): Type of event (e.g., 'join', 'leave').
            party_members (list): List of party members.
            is_party_paused (bool): Indicates if the party is paused.
            timestamp (datetime, optional): Timestamp of the log entry creation. Defaults to None.
        """
        if timestamp is None:
            self.timestamp = datetime.utcnow()  # UTC timestamp when the log entry is created
        else:
            self.timestamp = timestamp
        self.ign = ign
        self.event_type = event_type
        self.party_members = party_members
        self.is_party_paused = is_party_paused

    def to_dict(self):
        """
        Convert the log entry to a dictionary.

        Returns:
            dict: Dictionary representation of the log entry.
        """
        return {
            "timestamp": self.timestamp.strftime('%b %d, %Y %H:%M:%S GMT'),
            "ign": self.ign,
            "event_type": self.event_type,
            "party_members": self.party_members,
            "is_party_paused": self.is_party_paused
        }

    @staticmethod
    def from_dict(data):
        """
        Create a LogEntry object from a dictionary.

        Args:
            data (dict): Dictionary containing log entry data.
        Returns:
            LogEntry: LogEntry object created from the dictionary data.
        """
        return LogEntry(
            data["ign"],
            data["event_type"],
            data["party_members"],
            data["is_party_paused"],
            datetime.strptime(data["timestamp"], '%b %d, %Y %H:%M:%S GMT')
        )

class DataManager:
    def __init__(self, file_path='logs.json'):
        """
        Initialize the DataManager.

        Args:
            file_path (str, optional): File path for storing logs. Defaults to 'logs.json'.
        """
        self.file_path = file_path
        self.logs = []
        self.load_logs()
        self.last_operation = None

    def save_logs(self):
        """
        Save logs to a JSON file.
        """
        with open(self.file_path, 'w') as file:
            json.dump([log.to_dict() for log in self.logs], file)

    def load_logs(self):
        """
        Load logs from a JSON file.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                self.logs = [LogEntry.from_dict(entry) for entry in data]
        except FileNotFoundError:
            self.logs = []

    def add_log_entry(self, log_entry):
        """
        Add a log entry to the logs.

        Args:
            log_entry (LogEntry): Log entry object to be added.
        """
        self.logs.append(log_entry)
        self.save_logs()
        self.last_operation = ['add',[log_entry]]

    def add_log_entries(self, log_entries):
        """
        Add a list of log entries to the logs.

        Args:
            log_entries (List<LogEntry>): Log entry object to be added.
        """
        for log_entry in log_entries:
            self.logs.append(log_entry)
        self.save_logs()
        self.last_operation = ['add', log_entries]



    def get_logs_as_strings(self):
        """
        Get log entries as formatted strings.

        Returns:
            list: List of formatted log entry strings.
        """
        log_strings = []
        for log in self.logs:
            log_strings.append(f"{log.timestamp} - {log.ign if log.ign is not None else 'the leech'} {log.event_type}. leeching state: {'pausing' if log.is_party_paused else 'running'}")
        return log_strings

    def get_current_party_members(self):
        """
        Get the current party members based on the latest log entry.

        Returns:
            list: List of current party members or an empty list if no log entry is available.
        """
        if self.logs:
            latest_log_entry = self.logs[-1]
            return latest_log_entry.party_members
        else:
            return []
        
    def remove_logs_by_ign_event_type(self, ign, event_type):
        """
        Remove log entries based on In-Game Name (ign) and event type.

        Args:
            ign (str): In-Game Name of the player.
            event_type (str): Type of event (e.g., 'join', 'leave').
        Returns:
            int: Number of removed log entries.
        """
        removed_count = 0
        logs_to_remove = [log for log in self.logs if log.ign == ign and log.event_type == event_type]
        
        for log_entry in logs_to_remove:
            self.logs.remove(log_entry)
            removed_count += 1
        
        if removed_count > 0:
            self.save_logs()  # Save the modified logs after removal
        
        return removed_count
    
    def remove_log_entries(self, log_entries):
        """
        Remove a list of log entries from the logs.

        Args:
            log_entry (List<LogEntry>): The log entry to be removed.
        Returns:
            bool: True if the log entry was found and removed, False otherwise.
        """
        removed_logs =[]
        for log_entry in log_entries:
            if log_entry in self.logs:
                self.logs.remove(log_entry)
                removed_logs.append(log_entry)
 
        if len(removed_logs):
            self.save_logs()  # Save the modified logs after removal
            self.last_operation = ['remove',removed_logs]
