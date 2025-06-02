FROM grafana/grafana-enterprise:latest

COPY ./provisioning/datasources/ /etc/grafana/provisioning/datasources/

COPY ./provisioning/dashboards/ /etc/grafana/provisioning/dashboards/

COPY ./dashboard_jsons/ /var/lib/grafana/dashboards/provisioned/