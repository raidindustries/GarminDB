"""Class that manages Garmin Connect download config."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import os
import sys
import platform
import subprocess
import datetime
import tempfile

from idbutils import JsonConfig
from fitfile import Sport

from .statistics import Statistics
from idbutils import DbParams


class ConfigException(Exception):
    """Something unexpected happened while handling the configuration."""


class GarminConnectConfigManager(JsonConfig):
    """Class that manages Garmin Connect downloads."""

    temp_dir = tempfile.mkdtemp()
    homedir = os.path.expanduser('~')

    def __init__(self):
        """Return a new GarminConnectConfigManager instance."""
        self.enabled_statistics = None
        config_file = self.get_config_file()
        try:
            super().__init__(config_file)
        except Exception as e:
            print(str(e))
            print(rf"Missing or bad config: copy GarminConnectConfig.json.example from {os.path.dirname(os.path.abspath(__file__))} to {config_file} and edit it to add your Garmin Connect username and password.")
            sys.exit(-1)

    def get_node_value(self, node, leaf):
        node = self.config.get(node)
        if node is not None:
            return node.get(leaf)

    def get_node_value_default(self, node, leaf, default):
        node = self.config.get(node)
        if node is not None:
            return node.get(leaf, default)
        return default

    @classmethod
    def __create_dir_if_needed(cls, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    @classmethod
    def get_config_dir(cls):
        """
        Compute the configuration directory relative to the repository root.
        For your repo, climbing four levels up gets us to F:\projects\crypto\bitbucket\diet_tracker,
        and then we use the "garmindb" folder.
        """
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        config_dir = os.path.join(repo_root, "garmindb")
        return cls.__create_dir_if_needed(config_dir)

    def get_config_file(self):
        """Return the full path to the configuration file."""
        return os.path.join(self.get_config_dir(), 'GarminConnectConfig.json')

    @classmethod
    def get_session_file(cls):
        """Return the path to the session file."""
        return cls.get_config_dir() + os.sep + 'garth_session'

    def get_db_type(self):
        """Return the type (SQLite, MySQL, etc) of database that is configured."""
        return self.get_node_value_default('db', 'type', 'sqlite')

    def get_db_user(self):
        """Return the configured username of the database."""
        return self.get_node_value('db', 'user')

    def get_db_password(self):
        """Return the configured password of the database."""
        return self.get_node_value('db', 'password')

    def get_db_host(self):
        """Return the configured hostname of the database."""
        return self.get_node_value('db', 'host')

    def get_db_dir(self, test_dir=False):
        """Return the configured directory of where the database will be stored."""
        return self.__create_dir_if_needed(self.get_base_dir(test_dir) + os.sep + 'DBs')

    def get_db_params(self, test_db=False):
        """Return the database configuration."""
        db_type = self.get_db_type()
        db_params = {
            'db_type' : db_type
        }
        if db_type == 'sqlite':
            db_params['db_path'] = self.get_db_dir(test_db)
        elif db_type == "mysql":
            db_params['db_type'] = 'mysql'
            db_params['db_username'] = self.get_db_user()
            db_params['db_password'] = self.get_db_password()
            db_params['db_host'] = self.get_db_host()
        return DbParams(**db_params)

    def get_base_dir(self, test_dir=False):
        """Return the configured directory of where the data files will be stored."""
        base = self.get_node_value_default('directories', 'base_dir', 'HealthData')
        if test_dir:
            return self.temp_dir + os.sep + base
        if self.get_node_value_default('directories', 'relative_to_home', True):
            return self.__create_dir_if_needed(self.homedir + os.sep + base)
        return self.__create_dir_if_needed(base)

    def get_backup_dir(self):
        """Return the path to the backup directory."""
        return self.__create_dir_if_needed(self.get_base_dir() + os.sep + 'Backups')

    def __get_fit_files_dir(self, test_dir=False):
        return self.get_base_dir(test_dir) + os.sep + 'FitFiles'

    def get_fit_files_dir(self, test_dir=False):
        """Return the configured directory of where the FIT files will be stored creating it if needed."""
        return self.__create_dir_if_needed(self.__get_fit_files_dir(test_dir))

    def __get_monitoring_base_dir(self):
        return self.get_base_dir() + os.sep + 'FitFiles' + os.sep + 'Monitoring'

    def get_monitoring_base_dir(self):
        """
        Return the directory for monitoring data.
        If set in the config file (under directories->monitoring_base_dir), use that.
        Otherwise, default to a repository-relative path.
        """
        base = self.get_node_value('directories', 'monitoring_base_dir')
        if base:
            return base
        else:
            # Use repository-relative default: <repo_download_dir>/FitFiles/Monitoring
            return os.path.join(self.get_download_dir(), "FitFiles", "Monitoring")

    def get_monitoring_dir(self, year):
        monitoring_dir = os.path.join(self.get_download_dir(), "FitFiles", "Monitoring", str(year))  # Added FitFiles
        return self.__create_dir_if_needed(monitoring_dir)

    def get_activities_dir(self):
        """Return the directory for activities data."""
        activities_dir = os.path.join(self.get_download_dir(), "FitFiles", "Activities")  # Added FitFiles here
        return self.__create_dir_if_needed(activities_dir)

    def get_sleep_dir(self):
        """Return the configured directory of where the sleep files will be stored."""
        sleep_dir = os.path.join(self.get_download_dir(), "FitFiles", "Sleep")  # Added FitFiles here
        return self.__create_dir_if_needed(sleep_dir)

    def get_weight_dir(self):
        """Return the configured directory of where the weight files will be stored."""
        weight_dir = os.path.join(self.get_download_dir(), "FitFiles", "Weight")  # Added FitFiles here
        return self.__create_dir_if_needed(weight_dir)

    def get_rhr_dir(self):
        """Return the configured directory of where the resting heart rate files will be stored."""
        rhr_dir = os.path.join(self.get_download_dir(), "FitFiles", "Rhr")  # Added FitFiles here
        return self.__create_dir_if_needed(rhr_dir)

    def get_fitbit_dir(self):
        """Return the configured directory of where the FitBit will be stored."""
        fitbit_dir = os.path.join(self.get_download_dir(), "FitFiles", "FitBitFiles")  # Added FitFiles here
        return self.__create_dir_if_needed(fitbit_dir)

    def get_mshealth_dir(self):
        """Return the configured directory of where the Microsoft Health will be stored."""
        mshealth_dir = os.path.join(self.get_download_dir(), "FitFiles", "MSHealth")  # Added FitFiles here
        return self.__create_dir_if_needed(mshealth_dir)

    def get_plugins_dir(self):
        """Return the configured directory where the plugin files are located."""
        plugins_dir = os.path.join(self.get_download_dir(), "FitFiles", "Plugins")  # Added FitFiles here
        return self.__create_dir_if_needed(plugins_dir)

    def get_metric(self):
        """Return the unit system (metric, statute) that is configured."""
        return self.get_node_value_default('settings', 'metric', False)

    def get_secure_password(self):
        """Return the Garmin Connect password from secure storage. On MacOS that is the KeyChain."""
        system = platform.system()
        if system == 'Darwin':
            # This relies on there being a 'internet password' entry for URL https://sso.garmin.com in the login keychain
            domain = 'sso.garmin.com'
            try:
                password = subprocess.check_output(["security", "find-internet-password", "-s", domain, "-w"])
                if password:
                    return password.rstrip()
            except Exception:
                pass
            raise ConfigException(f'Secure password was specified but no "Internet Password" entry was found in the Login Keychain for https://{domain}')

    def get_user(self):
        """Return the Garmin Connect username."""
        return self.get_node_value('credentials', 'user')

    def get_password(self):
        """Return the Garmin Connect password."""
        if self.get_node_value_default('credentials', 'secure_password', False):
            return self.get_secure_password()
        return self.get_node_value('credentials', 'password')

    def get_garmin_base_domain(self):
        """Return the Garmin base domain to use for api calls."""
        return self.get_node_value_default('garmin', 'domain', "garmin.com")

    def default_display_activities(cls):
        """Return a list of the default activities to display."""
        return [Sport.strict_from_string(activity) for activity in super().default_display_activities]

    def latest_activity_count(self):
        """Return the number of activities to download when getting the latest."""
        return self.get_node_value('data', 'download_latest_activities')

    def all_activity_count(self):
        """Return the number of activities to download when getting all activities."""
        return self.get_node_value('data', 'download_all_activities')

    def stat_start_date(self, stat_type):
        """Return a tuple containing the start date and the number of days to fetch stats from."""
        date = self.get_node_value('data', stat_type + '_start_date')
        days = (datetime.datetime.now().date() - date).days
        return (date, days)

    def device_mount_dir(self):
        """Return the directory where the Garmin USB device is mounted."""
        return self.get_node_value('directories', 'mount_dir')

    def __device_garmin_dir(self):
        return self.device_mount_dir() + os.sep + 'garmin'

    def device_settings_dir(self):
        """Return the full path to the settings file on a mounted device."""
        return self.__device_garmin_dir() + os.sep + 'settings'

    def device_monitoring_dir(self):
        """Return the full path to the monitoring files on a mounted device."""
        return self.__device_garmin_dir() + os.sep + 'monitor'

    def device_sleep_dir(self):
        """Return the full path to the sleep files on a mounted device."""
        return self.__device_garmin_dir() + os.sep + 'sleep'

    def device_activities_dir(self):
        """Return the full path to the activities files on a mounted device."""
        return self.__device_garmin_dir() + os.sep + 'activity'

    def download_days_overlap(self):
        """Return the number of days to overlap previously downloaded data when downloading."""
        return self.get_node_value('data', 'download_days_overlap')

    def course_views(self, type):
        """Return a list of course ids to create views for for the given activitiy type."""
        return self.get_node_value('course_views', type)

    def is_stat_enabled(self, statistic):
        """Return whether a particular statistic is enabled or not."""
        return statistic in self.enabled_stats()

    def enabled_stats(self):
        """Return all enabled statistics as a list of string names."""
        if not self.enabled_statistics:
            json_enabled_stats_dict = self.config.get('enabled_stats', {stat_name: True for stat_name in list(Statistics)})
            self.enabled_statistics = [Statistics.from_string(stat_name) for stat_name, stat_enabled in json_enabled_stats_dict.items() if stat_enabled]
        return self.enabled_statistics

    def display_activities(self):
        """Return a list of activities to display."""
        activities_list = self.get_node_value('activities', 'display')
        if not activities_list:
            activities_list = self.get_node_value_default('settings', 'default_display_activities', [])
        return [Sport.strict_from_string(activity) for activity in activities_list]

    @classmethod
    def get_download_dir(cls):
        """Get download directory from environment or use a default based on the config directory."""
        download_base = os.environ.get("DOWNLOAD_BASE_DIR")
        if download_base:
            print(f"Using DOWNLOAD_BASE_DIR from environment: {download_base}")
            return cls.__create_dir_if_needed(download_base)
        else:
            # Fallback: use the config directory joined with 'download'
            default_base = os.path.join(cls.get_config_dir(), "download")
            print(f"DOWNLOAD_BASE_DIR not set. Using default download directory: {default_base}")
            return cls.__create_dir_if_needed(default_base)
