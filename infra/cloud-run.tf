# resource "google_cloud_run_v2_job" "default" {
#   name     = "cloudrun-job"
#   location = "us-central1"

#   template {
#     template {
#       containers {
#         image = "gcr.io/phone-numbers-335120/gettr:latest"
        
#         env {
#           name  = "USERNAME"
#           value = "chainsawmexican"
#         }     
#       }
#     }
#   }
# }