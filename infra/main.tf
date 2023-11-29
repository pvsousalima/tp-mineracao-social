resource "google_compute_instance" "my_instance" {
  name         = "my-instance"
  machine_type = "e2-medium"  # Replace with your desired instance type
  zone         = "us-central1-a"  # Replace with your desired GCP zone
  tags         = ["http-server", "https-server"]
  deletion_protection = false

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  scheduling {
    automatic_restart = false
    preemptible       = true
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    sudo apt-get update -y
    sudo apt-get install -y docker.io

    # Add the current user to the docker group to run docker without sudo
    sudo usermod -aG docker $USER

    # Restart Docker to apply group membership changes
    sudo systemctl restart docker
    sudo apt install python3-pip -y
    pip3 install pandas psycopg2-binary
  EOF
}
