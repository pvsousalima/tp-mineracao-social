provider "google" {
  project = "phone-numbers-335120"
  region  = "us-central1"  # Replace with your desired GCP region
}

resource "google_sql_database_instance" "my_database_instance" {
  name             = "my-database-instance"
  database_version = "POSTGRES_9_6"  # Specify the PostgreSQL version you want
  region           = "us-central1"    # Replace with your desired GCP region

  settings {
    tier = "db-f1-micro"  # Small CPU and 100GB storage
    
    # Allow all incoming connections (0.0.0.0/0)
    ip_configuration {
      ipv4_enabled    = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }
}

resource "google_sql_database" "my_database" {
  name     = "my-database"
  instance = google_sql_database_instance.my_database_instance.name
  charset  = "UTF8"  # Codificação UTF-8
  collation = "en_US.UTF8"  # Localidade correta para UTF-8
}

resource "google_sql_user" "my_database_user1" {
  name     = "my-database-user1"
  instance = google_sql_database_instance.my_database_instance.name
  password = "my-password"  # Replace with your desired password
}

output "db_config" {
  description = "Database configuration for Google Cloud SQL"

  value = {
    host     = google_sql_database_instance.my_database_instance.ip_address,
    user     = google_sql_user.my_database_user1.name,
    password = "my-password",  # Replace with your actual database password
    database = google_sql_database.my_database.name,
  }
}
