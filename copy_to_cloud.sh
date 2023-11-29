# gcloud compute scp --recurse ./src my-instance:./ --zone us-central1-a 
gcloud compute ssh my-instance --zone=us-central1-a --command "mkdir src"
gcloud compute scp --recurse ./src/followers.py my-instance:./src/followers.py --zone us-central1-a 
gcloud compute scp --recurse ./src/get.py my-instance:./src/get.py --zone us-central1-a 
gcloud compute scp --recurse ./src/usernames.txt my-instance:./src/usernames.txt --zone us-central1-a 
gcloud compute scp --recurse ./src/t.sh my-instance:./src/t.sh --zone us-central1-a 
gcloud compute ssh my-instance --zone=us-central1-a --command "sudo apt install python3-pip -y; pip3 install pandas psycopg2-binary; cd src; sudo sh t.sh"
