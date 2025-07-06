import pytest
import os
from unittest.mock import patch
from config import Config, DevelopmentConfig, ProductionConfig, ConfigTesting, config


class TestConfigBase:
    """Test the base Config class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Save original environment variables
        self.original_env = {}
        env_vars = [
            'SECRET_KEY', 'DATABASE_URL', 'LOG_LEVEL', 'LOG_DIR', 
            'REQUEST_LOGGING_ENABLED', 'LOG_RETENTION_DAYS', 
            'LOG_MAX_BYTES', 'LOG_BACKUP_COUNT'
        ]
        
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original environment variables
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_config_default_values(self):
        """Test Config class default values."""
        config_obj = Config()
        
        # Test default values
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
        assert config_obj.LOG_LEVEL == 'INFO'
        assert config_obj.LOG_DIR == 'logs'
        assert config_obj.REQUEST_LOGGING_ENABLED is True
        assert config_obj.LOG_RETENTION_DAYS == 30
        assert config_obj.LOG_MAX_BYTES == 10485760  # 10MB
        assert config_obj.LOG_BACKUP_COUNT == 5
    
    def test_config_with_environment_variables(self):
        """Test Config class with environment variables."""
        # Set environment variables
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/testdb'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['LOG_DIR'] = '/var/log/app'
        os.environ['REQUEST_LOGGING_ENABLED'] = 'false'
        os.environ['LOG_RETENTION_DAYS'] = '60'
        os.environ['LOG_MAX_BYTES'] = '20971520'  # 20MB
        os.environ['LOG_BACKUP_COUNT'] = '10'
        
        config_obj = Config()
        
        # Test values from environment
        assert config_obj.SECRET_KEY == 'test-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'postgresql://user:pass@localhost/testdb'
        assert config_obj.LOG_LEVEL == 'DEBUG'
        assert config_obj.LOG_DIR == '/var/log/app'
        assert config_obj.REQUEST_LOGGING_ENABLED is False
        assert config_obj.LOG_RETENTION_DAYS == 60
        assert config_obj.LOG_MAX_BYTES == 20971520
        assert config_obj.LOG_BACKUP_COUNT == 10
    
    def test_config_request_logging_enabled_parsing(self):
        """Test REQUEST_LOGGING_ENABLED parsing from environment."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('', False),
            ('invalid', False),
        ]
        
        for env_value, expected in test_cases:
            os.environ['REQUEST_LOGGING_ENABLED'] = env_value
            config_obj = Config()
            assert config_obj.REQUEST_LOGGING_ENABLED == expected, f"Failed for input '{env_value}'"
            del os.environ['REQUEST_LOGGING_ENABLED']
    
    def test_config_integer_parsing(self):
        """Test integer parsing from environment variables."""
        # Test valid integers
        os.environ['LOG_RETENTION_DAYS'] = '45'
        os.environ['LOG_MAX_BYTES'] = '15728640'
        os.environ['LOG_BACKUP_COUNT'] = '7'
        
        config_obj = Config()
        
        assert config_obj.LOG_RETENTION_DAYS == 45
        assert config_obj.LOG_MAX_BYTES == 15728640
        assert config_obj.LOG_BACKUP_COUNT == 7
    
    def test_config_invalid_integer_parsing(self):
        """Test invalid integer parsing from environment variables."""
        # Test invalid integers (should raise ValueError)
        os.environ['LOG_RETENTION_DAYS'] = 'not-a-number'
        
        with pytest.raises(ValueError):
            Config()
    
    def test_config_missing_optional_env_vars(self):
        """Test Config behavior when optional environment variables are missing."""
        # All environment variables are optional and have defaults
        config_obj = Config()
        
        # Should not raise any exceptions
        assert config_obj.SECRET_KEY is not None
        assert config_obj.SQLALCHEMY_DATABASE_URI is not None
        assert config_obj.LOG_LEVEL is not None
        assert config_obj.LOG_DIR is not None
        assert isinstance(config_obj.REQUEST_LOGGING_ENABLED, bool)
        assert isinstance(config_obj.LOG_RETENTION_DAYS, int)
        assert isinstance(config_obj.LOG_MAX_BYTES, int)
        assert isinstance(config_obj.LOG_BACKUP_COUNT, int)
    
    def test_config_sqlalchemy_track_modifications_always_false(self):
        """Test that SQLALCHEMY_TRACK_MODIFICATIONS is always False."""
        config_obj = Config()
        
        # Should always be False regardless of environment
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
    
    def test_config_inheritance_structure(self):
        """Test that Config class can be inherited properly."""
        class TestConfig(Config):
            TEST_VALUE = 'test'
        
        config_obj = TestConfig()
        
        # Should inherit base config values
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
        
        # Should have custom value
        assert config_obj.TEST_VALUE == 'test'


class TestDevelopmentConfig:
    """Test the DevelopmentConfig class."""
    
    def test_development_config_inherits_from_config(self):
        """Test that DevelopmentConfig inherits from Config."""
        assert issubclass(DevelopmentConfig, Config)
    
    def test_development_config_debug_enabled(self):
        """Test that DevelopmentConfig has debug enabled."""
        config_obj = DevelopmentConfig()
        
        assert config_obj.DEBUG is True
    
    def test_development_config_log_level_debug(self):
        """Test that DevelopmentConfig has DEBUG log level."""
        config_obj = DevelopmentConfig()
        
        assert config_obj.LOG_LEVEL == 'DEBUG'
    
    def test_development_config_inherits_base_values(self):
        """Test that DevelopmentConfig inherits base Config values."""
        config_obj = DevelopmentConfig()
        
        # Should inherit from base Config
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
        assert config_obj.LOG_DIR == 'logs'
        assert config_obj.REQUEST_LOGGING_ENABLED is True
    
    def test_development_config_with_environment_variables(self):
        """Test DevelopmentConfig with environment variables."""
        os.environ['SECRET_KEY'] = 'dev-env-secret'
        os.environ['DATABASE_URL'] = 'sqlite:///dev.db'
        
        config_obj = DevelopmentConfig()
        
        # Should use environment values
        assert config_obj.SECRET_KEY == 'dev-env-secret'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///dev.db'
        
        # Should keep development-specific values
        assert config_obj.DEBUG is True
        assert config_obj.LOG_LEVEL == 'DEBUG'
        
        # Clean up
        del os.environ['SECRET_KEY']
        del os.environ['DATABASE_URL']


class TestProductionConfig:
    """Test the ProductionConfig class."""
    
    def test_production_config_inherits_from_config(self):
        """Test that ProductionConfig inherits from Config."""
        assert issubclass(ProductionConfig, Config)
    
    def test_production_config_debug_disabled(self):
        """Test that ProductionConfig has debug disabled."""
        config_obj = ProductionConfig()
        
        assert config_obj.DEBUG is False
    
    def test_production_config_log_level_info(self):
        """Test that ProductionConfig has INFO log level."""
        config_obj = ProductionConfig()
        
        assert config_obj.LOG_LEVEL == 'INFO'
    
    def test_production_config_inherits_base_values(self):
        """Test that ProductionConfig inherits base Config values."""
        config_obj = ProductionConfig()
        
        # Should inherit from base Config
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
        assert config_obj.LOG_DIR == 'logs'
        assert config_obj.REQUEST_LOGGING_ENABLED is True
    
    def test_production_config_with_environment_variables(self):
        """Test ProductionConfig with environment variables."""
        os.environ['SECRET_KEY'] = 'prod-secret-key'
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@prod-db/app'
        
        config_obj = ProductionConfig()
        
        # Should use environment values
        assert config_obj.SECRET_KEY == 'prod-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'postgresql://user:pass@prod-db/app'
        
        # Should keep production-specific values
        assert config_obj.DEBUG is False
        assert config_obj.LOG_LEVEL == 'INFO'
        
        # Clean up
        del os.environ['SECRET_KEY']
        del os.environ['DATABASE_URL']


class TestConfigTesting:
    """Test the ConfigTesting class."""
    
    def test_testing_config_inherits_from_config(self):
        """Test that ConfigTesting inherits from Config."""
        assert issubclass(ConfigTesting, Config)
    
    def test_testing_config_testing_enabled(self):
        """Test that ConfigTesting has testing enabled."""
        config_obj = ConfigTesting()
        
        assert config_obj.TESTING is True
    
    def test_testing_config_database_in_memory(self):
        """Test that ConfigTesting uses in-memory database."""
        config_obj = ConfigTesting()
        
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    
    def test_testing_config_csrf_disabled(self):
        """Test that ConfigTesting has CSRF disabled."""
        config_obj = ConfigTesting()
        
        assert config_obj.WTF_CSRF_ENABLED is False
    
    def test_testing_config_request_logging_disabled(self):
        """Test that ConfigTesting has request logging disabled."""
        config_obj = ConfigTesting()
        
        assert config_obj.REQUEST_LOGGING_ENABLED is False
    
    def test_testing_config_log_level_warning(self):
        """Test that ConfigTesting has WARNING log level."""
        config_obj = ConfigTesting()
        
        assert config_obj.LOG_LEVEL == 'WARNING'
    
    def test_testing_config_inherits_base_values(self):
        """Test that ConfigTesting inherits base Config values."""
        config_obj = ConfigTesting()
        
        # Should inherit from base Config
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
        assert config_obj.LOG_DIR == 'logs'
    
    def test_testing_config_overrides_environment_database(self):
        """Test that ConfigTesting overrides environment DATABASE_URL."""
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/testdb'
        
        config_obj = ConfigTesting()
        
        # Should use in-memory database regardless of environment
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
        
        # Clean up
        del os.environ['DATABASE_URL']
    
    def test_testing_config_overrides_environment_request_logging(self):
        """Test that ConfigTesting overrides environment REQUEST_LOGGING_ENABLED."""
        os.environ['REQUEST_LOGGING_ENABLED'] = 'true'
        
        config_obj = ConfigTesting()
        
        # Should disable request logging regardless of environment
        assert config_obj.REQUEST_LOGGING_ENABLED is False
        
        # Clean up
        del os.environ['REQUEST_LOGGING_ENABLED']


class TestConfigDictionary:
    """Test the config dictionary and its mappings."""
    
    def test_config_dictionary_structure(self):
        """Test that config dictionary has expected structure."""
        assert isinstance(config, dict)
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        assert 'default' in config
    
    def test_config_dictionary_mappings(self):
        """Test that config dictionary maps to correct classes."""
        assert config['development'] == DevelopmentConfig
        assert config['production'] == ProductionConfig
        assert config['testing'] == ConfigTesting
        assert config['default'] == DevelopmentConfig
    
    def test_config_dictionary_instantiation(self):
        """Test that config dictionary classes can be instantiated."""
        for config_name, config_class in config.items():
            config_obj = config_class()
            assert isinstance(config_obj, Config)
    
    def test_config_selection_by_environment(self):
        """Test selecting config by environment name."""
        # Test each environment
        environments = ['development', 'production', 'testing', 'default']
        
        for env in environments:
            config_class = config[env]
            config_obj = config_class()
            
            # Should be a valid config instance
            assert isinstance(config_obj, Config)
            assert hasattr(config_obj, 'SECRET_KEY')
            assert hasattr(config_obj, 'SQLALCHEMY_DATABASE_URI')
    
    def test_config_default_is_development(self):
        """Test that default config is development config."""
        assert config['default'] == config['development']
        assert config['default'] == DevelopmentConfig
    
    def test_config_environment_specific_properties(self):
        """Test that each environment has its specific properties."""
        # Development
        dev_config = config['development']()
        assert dev_config.DEBUG is True
        assert dev_config.LOG_LEVEL == 'DEBUG'
        
        # Production
        prod_config = config['production']()
        assert prod_config.DEBUG is False
        assert prod_config.LOG_LEVEL == 'INFO'
        
        # Testing
        test_config = config['testing']()
        assert test_config.TESTING is True
        assert test_config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
        assert test_config.REQUEST_LOGGING_ENABLED is False
        assert test_config.LOG_LEVEL == 'WARNING'


class TestConfigEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_config_with_empty_environment_variables(self):
        """Test Config with empty environment variables."""
        os.environ['SECRET_KEY'] = ''
        os.environ['DATABASE_URL'] = ''
        os.environ['LOG_DIR'] = ''
        
        config_obj = Config()
        
        # Should use defaults when environment variables are empty
        assert config_obj.SECRET_KEY == 'dev-secret-key'
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'
        assert config_obj.LOG_DIR == 'logs'
        
        # Clean up
        del os.environ['SECRET_KEY']
        del os.environ['DATABASE_URL']
        del os.environ['LOG_DIR']
    
    def test_config_with_zero_values(self):
        """Test Config with zero values in environment."""
        os.environ['LOG_RETENTION_DAYS'] = '0'
        os.environ['LOG_MAX_BYTES'] = '0'
        os.environ['LOG_BACKUP_COUNT'] = '0'
        
        config_obj = Config()
        
        # Should accept zero values
        assert config_obj.LOG_RETENTION_DAYS == 0
        assert config_obj.LOG_MAX_BYTES == 0
        assert config_obj.LOG_BACKUP_COUNT == 0
        
        # Clean up
        del os.environ['LOG_RETENTION_DAYS']
        del os.environ['LOG_MAX_BYTES']
        del os.environ['LOG_BACKUP_COUNT']
    
    def test_config_with_negative_values(self):
        """Test Config with negative values in environment."""
        os.environ['LOG_RETENTION_DAYS'] = '-1'
        os.environ['LOG_MAX_BYTES'] = '-1000'
        os.environ['LOG_BACKUP_COUNT'] = '-5'
        
        config_obj = Config()
        
        # Should accept negative values (though they may not make sense)
        assert config_obj.LOG_RETENTION_DAYS == -1
        assert config_obj.LOG_MAX_BYTES == -1000
        assert config_obj.LOG_BACKUP_COUNT == -5
        
        # Clean up
        del os.environ['LOG_RETENTION_DAYS']
        del os.environ['LOG_MAX_BYTES']
        del os.environ['LOG_BACKUP_COUNT']
    
    def test_config_with_very_large_values(self):
        """Test Config with very large values in environment."""
        os.environ['LOG_RETENTION_DAYS'] = '999999'
        os.environ['LOG_MAX_BYTES'] = '1073741824'  # 1GB
        os.environ['LOG_BACKUP_COUNT'] = '100'
        
        config_obj = Config()
        
        # Should accept large values
        assert config_obj.LOG_RETENTION_DAYS == 999999
        assert config_obj.LOG_MAX_BYTES == 1073741824
        assert config_obj.LOG_BACKUP_COUNT == 100
        
        # Clean up
        del os.environ['LOG_RETENTION_DAYS']
        del os.environ['LOG_MAX_BYTES']
        del os.environ['LOG_BACKUP_COUNT']
    
    def test_config_attribute_access(self):
        """Test that config attributes can be accessed like class attributes."""
        config_obj = Config()
        
        # Test that attributes exist and are accessible
        assert hasattr(config_obj, 'SECRET_KEY')
        assert hasattr(config_obj, 'SQLALCHEMY_DATABASE_URI')
        assert hasattr(config_obj, 'SQLALCHEMY_TRACK_MODIFICATIONS')
        assert hasattr(config_obj, 'LOG_LEVEL')
        assert hasattr(config_obj, 'LOG_DIR')
        assert hasattr(config_obj, 'REQUEST_LOGGING_ENABLED')
        assert hasattr(config_obj, 'LOG_RETENTION_DAYS')
        assert hasattr(config_obj, 'LOG_MAX_BYTES')
        assert hasattr(config_obj, 'LOG_BACKUP_COUNT')
        
        # Test that we can read the values
        _ = config_obj.SECRET_KEY
        _ = config_obj.SQLALCHEMY_DATABASE_URI
        _ = config_obj.LOG_LEVEL
    
    def test_config_immutability(self):
        """Test that config values can be modified after instantiation."""
        config_obj = Config()
        
        original_secret = config_obj.SECRET_KEY
        
        # Modify the config
        config_obj.SECRET_KEY = 'new-secret-key'
        
        # Should be modified
        assert config_obj.SECRET_KEY == 'new-secret-key'
        assert config_obj.SECRET_KEY != original_secret 