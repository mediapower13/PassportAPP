"""
Database migration utilities for PassportApp
Handle database schema migrations and version control
"""

from datetime import datetime
import os
import hashlib


class Migration:
    """Base migration class"""
    
    def __init__(self, version, description):
        self.version = version
        self.description = description
        self.timestamp = datetime.utcnow()
    
    def up(self, db):
        """Apply migration"""
        raise NotImplementedError("Subclasses must implement up()")
    
    def down(self, db):
        """Rollback migration"""
        raise NotImplementedError("Subclasses must implement down()")


class MigrationManager:
    """Manage database migrations"""
    
    def __init__(self, db, migrations_dir='migrations'):
        self.db = db
        self.migrations_dir = migrations_dir
        self.migrations = []
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table if not exists"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        )
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(create_table_sql)
            self.db.commit()
        except Exception as e:
            print(f"Error creating migrations table: {e}")
            self.db.rollback()
    
    def register_migration(self, migration):
        """Register a migration"""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting applied migrations: {e}")
            return []
    
    def get_pending_migrations(self):
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied]
    
    def apply_migration(self, migration):
        """Apply a single migration"""
        try:
            print(f"Applying migration {migration.version}: {migration.description}")
            
            # Apply migration
            migration.up(self.db)
            
            # Record migration
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                (migration.version, migration.description)
            )
            self.db.commit()
            
            print(f"Migration {migration.version} applied successfully")
            return True
        
        except Exception as e:
            print(f"Error applying migration {migration.version}: {e}")
            self.db.rollback()
            return False
    
    def rollback_migration(self, migration):
        """Rollback a single migration"""
        try:
            print(f"Rolling back migration {migration.version}: {migration.description}")
            
            # Rollback migration
            migration.down(self.db)
            
            # Remove migration record
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (migration.version,))
            self.db.commit()
            
            print(f"Migration {migration.version} rolled back successfully")
            return True
        
        except Exception as e:
            print(f"Error rolling back migration {migration.version}: {e}")
            self.db.rollback()
            return False
    
    def migrate_up(self, target_version=None):
        """Apply all pending migrations up to target version"""
        pending = self.get_pending_migrations()
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        if not pending:
            print("No pending migrations")
            return True
        
        print(f"Applying {len(pending)} migrations...")
        
        for migration in pending:
            if not self.apply_migration(migration):
                return False
        
        print("All migrations applied successfully")
        return True
    
    def migrate_down(self, steps=1):
        """Rollback last N migrations"""
        applied = self.get_applied_migrations()
        
        if not applied:
            print("No migrations to rollback")
            return True
        
        # Get last N applied migrations
        to_rollback = applied[-steps:]
        
        print(f"Rolling back {len(to_rollback)} migrations...")
        
        # Rollback in reverse order
        for version in reversed(to_rollback):
            migration = next((m for m in self.migrations if m.version == version), None)
            
            if migration:
                if not self.rollback_migration(migration):
                    return False
            else:
                print(f"Warning: Migration {version} not found in registered migrations")
        
        print("Rollback completed")
        return True
    
    def get_migration_status(self):
        """Get migration status"""
        applied = set(self.get_applied_migrations())
        
        status = {
            'total': len(self.migrations),
            'applied': len(applied),
            'pending': len(self.migrations) - len(applied),
            'migrations': []
        }
        
        for migration in self.migrations:
            status['migrations'].append({
                'version': migration.version,
                'description': migration.description,
                'applied': migration.version in applied
            })
        
        return status


# Example migrations
class CreateUsersTable(Migration):
    """Create users table"""
    
    def __init__(self):
        super().__init__('001', 'Create users table')
    
    def up(self, db):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            wallet_address VARCHAR(42),
            is_premium BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor = db.cursor()
        cursor.execute(sql)
    
    def down(self, db):
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")


class CreatePassportsTable(Migration):
    """Create passports table"""
    
    def __init__(self):
        super().__init__('002', 'Create passports table')
    
    def up(self, db):
        sql = """
        CREATE TABLE IF NOT EXISTS passports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            passport_number VARCHAR(50) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            date_of_birth DATE NOT NULL,
            nationality VARCHAR(100) NOT NULL,
            issue_date DATE NOT NULL,
            expiry_date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        cursor = db.cursor()
        cursor.execute(sql)
    
    def down(self, db):
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS passports")


class CreateNFTsTable(Migration):
    """Create NFTs table"""
    
    def __init__(self):
        super().__init__('003', 'Create NFTs table')
    
    def up(self, db):
        sql = """
        CREATE TABLE IF NOT EXISTS nfts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id INTEGER UNIQUE NOT NULL,
            passport_id INTEGER NOT NULL,
            owner_address VARCHAR(42) NOT NULL,
            metadata_uri TEXT,
            ipfs_hash VARCHAR(100),
            listed BOOLEAN DEFAULT FALSE,
            price DECIMAL(18, 8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passport_id) REFERENCES passports(id) ON DELETE CASCADE
        )
        """
        cursor = db.cursor()
        cursor.execute(sql)
    
    def down(self, db):
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS nfts")


class CreateTransactionsTable(Migration):
    """Create transactions table"""
    
    def __init__(self):
        super().__init__('004', 'Create transactions table')
    
    def up(self, db):
        sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_hash VARCHAR(66) UNIQUE NOT NULL,
            from_address VARCHAR(42) NOT NULL,
            to_address VARCHAR(42) NOT NULL,
            value DECIMAL(18, 8),
            gas_used INTEGER,
            gas_price DECIMAL(18, 8),
            block_number INTEGER,
            status VARCHAR(20),
            tx_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor = db.cursor()
        cursor.execute(sql)
    
    def down(self, db):
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS transactions")


class AddIndexesToTables(Migration):
    """Add indexes for performance"""
    
    def __init__(self):
        super().__init__('005', 'Add indexes to tables')
    
    def up(self, db):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address)",
            "CREATE INDEX IF NOT EXISTS idx_passports_user ON passports(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_passports_number ON passports(passport_number)",
            "CREATE INDEX IF NOT EXISTS idx_nfts_token ON nfts(token_id)",
            "CREATE INDEX IF NOT EXISTS idx_nfts_owner ON nfts(owner_address)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(tx_hash)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_from ON transactions(from_address)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_to ON transactions(to_address)"
        ]
        
        cursor = db.cursor()
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def down(self, db):
        indexes = [
            "DROP INDEX IF EXISTS idx_users_email",
            "DROP INDEX IF EXISTS idx_users_wallet",
            "DROP INDEX IF EXISTS idx_passports_user",
            "DROP INDEX IF EXISTS idx_passports_number",
            "DROP INDEX IF EXISTS idx_nfts_token",
            "DROP INDEX IF EXISTS idx_nfts_owner",
            "DROP INDEX IF EXISTS idx_transactions_hash",
            "DROP INDEX IF EXISTS idx_transactions_from",
            "DROP INDEX IF EXISTS idx_transactions_to"
        ]
        
        cursor = db.cursor()
        for index_sql in indexes:
            cursor.execute(index_sql)


def init_migrations(db):
    """Initialize migration manager with all migrations"""
    manager = MigrationManager(db)
    
    # Register all migrations
    manager.register_migration(CreateUsersTable())
    manager.register_migration(CreatePassportsTable())
    manager.register_migration(CreateNFTsTable())
    manager.register_migration(CreateTransactionsTable())
    manager.register_migration(AddIndexesToTables())
    
    return manager


def run_migrations(db):
    """Run all pending migrations"""
    manager = init_migrations(db)
    return manager.migrate_up()


def rollback_migrations(db, steps=1):
    """Rollback last N migrations"""
    manager = init_migrations(db)
    return manager.migrate_down(steps)
