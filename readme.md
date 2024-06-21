## ads

Post regular events to https://www.hueckelhoven.de/freizeit-und-kultur/veranstaltungen/

Run

```sh
# softlink ~/bin/ff -> fill_form.py
ff
ff post ela 0
ff resize
```

## vocab

Enable google APIs: https://console.cloud.google.com/flows/enableapi?apiid=translate.googleapis.com

Create google service account (api key equivalent):

```bash
# install and init gcloud
trizen -S google-cloud-cli
gcloud init
gcloud auth application-default login

# create service account
gcloud config set project deutsch-training-413809
gcloud iam service-accounts create deutsch-training-service \
    --description="API access to transcription and translation." \
    --display-name="Deutsch Training Service"
# add translate api permission
gcloud projects add-iam-policy-binding deutsch-training-413809 \
    --member="serviceAccount:deutsch-training-service@deutsch-training-413809.iam.gserviceaccount.com" \
    --role="roles/cloudtranslate.user"
```

Initial setup

```bash
# initial setup
python -m hh-adabru ~/.venv
. ~/.venv/bin/activate
pip install fpdf google-cloud-translate

# print next page
./vocab/print_page.py
```
