## Week 1 Homework PartB

In this homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP install Terraform. Copy the files from the course repo
[here](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup/1_terraform_gcp/terraform) to your VM.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

## Question 1: Enter the Output Displayed After Running Terraform Apply

Run the command to get information on Docker

>Proposed Command:
```
terraform apply -var="project=gentle-presence-375809"
```

Output:

    Terraform used the selected providers to generate the following execution plan.
    Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

      # google_bigquery_dataset.dataset will be created
      + resource "google_bigquery_dataset" "dataset" {
          + creation_time              = (known after apply)
          + dataset_id                 = "trips_data_all"
          + delete_contents_on_destroy = false
          + etag                       = (known after apply)
          + id                         = (known after apply)
          + labels                     = (known after apply)
          + last_modified_time         = (known after apply)
          + location                   = "europe-west6"
          + project                    = "gentle-presence-375809"
          + self_link                  = (known after apply)

          + access {
              + domain         = (known after apply)
              + group_by_email = (known after apply)
              + role           = (known after apply)
              + special_group  = (known after apply)
              + user_by_email  = (known after apply)

              + dataset {
                  + target_types = (known after apply)

                  + dataset {
                      + dataset_id = (known after apply)
                      + project_id = (known after apply)
                    }
                }

              + routine {
                  + dataset_id = (known after apply)
                  + project_id = (known after apply)
                  + routine_id = (known after apply)
                }

              + view {
                  + dataset_id = (known after apply)
                  + project_id = (known after apply)
                  + table_id   = (known after apply)
                }
            }
        }

      # google_storage_bucket.data-lake-bucket will be created
      + resource "google_storage_bucket" "data-lake-bucket" {
          + force_destroy               = true
          + id                          = (known after apply)
          + location                    = "EUROPE-WEST6"
          + name                        = "dtc_data_lake_gentle-presence-375809"
          + project                     = (known after apply)
          + public_access_prevention    = (known after apply)
          + self_link                   = (known after apply)
          + storage_class               = "STANDARD"
          + uniform_bucket_level_access = true
          + url                         = (known after apply)

          + lifecycle_rule {
              + action {
                  + type = "Delete"
                }

              + condition {
                  + age                   = 30
                  + matches_prefix        = []
                  + matches_storage_class = []
                  + matches_suffix        = []
                  + with_state            = (known after apply)
                }
            }

          + versioning {
              + enabled = true
            }

          + website {
              + main_page_suffix = (known after apply)
              + not_found_page   = (known after apply)
            }
        }

    Plan: 2 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    google_bigquery_dataset.dataset: Creating...
    google_storage_bucket.data-lake-bucket: Creating...
    google_storage_bucket.data-lake-bucket: Creation complete after 1s [id=dtc_data_lake_gentle-presence-375809]
    google_bigquery_dataset.dataset: Creation complete after 1s [id=projects/gentle-presence-375809/datasets/trips_data_all]
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

## Submitting the solutions

* Form for submitting: [form](https://forms.gle/S57Xs3HL9nB3YTzj9)
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 26 January (Thursday), 22:00 CET
