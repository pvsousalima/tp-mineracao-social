gcloud compute scp --recurse ./src my-instance:./ --zone us-central1-a 
# gcloud compute ssh --zone "us-central1-a" "my-instance" --project "phone-numbers-335120" ;
# rsync -ravz -e "gcloud compute ssh my-instance --quiet --command" /src my-instance:./
gcloud compute ssh my-instance --zone=us-central1-a --command "USERNAME=siren_pearl sudo sh src/run.sh"
