# rss everything

Integrate usefull rss services in one docker-compose.yml

## Pre-setups

Create `n8n-scripts` and `n8n-files` directories, and `chmod` to 777

## Usefull docker commands

manually build image after dockerfile changed

- `docker compose build`

update

- `docker compose pull`

check status

- `docker ps`

run containers

- `docker compose up -d --remove-orphans`

stop containers

- `docker compose down --remove-orphans`

start an interactive shell session inside container

- `docker exec -it [CONTAINER_ID_OR_NAME] /bin/sh`
- `exit` or `ctrl-d`

## Reverse proxy for subdomain

We use caddy as reverse proxy for subdomain. Copy the `Caddyfile` to
`/etc/caddy/Caddyfile` and reload caddy.

```bash
# start/stop caddy
systemctl enable caddy
systemctl start caddy
systemctl stop caddy

# update the default Caddyfile
nvim /etc/caddy/Caddyfile

# check Caddyfile syntax
caddy validate --config /etc/caddy/Caddyfile
caddy fmt --overwrite /etc/caddy/Caddyfile

# ensure appropriate permissions to the web root
groups caddy
chown -R caddy:www-data /root/rss-everything/html

chmod 755 /root
cmmod 755 /root/rss-everything
sudo chmod -R 755 /root/rss-everything/html

# reload Caddy
systemctl reload caddy
```

## Migrate volumes to new server

Based on the [docker documentation] and this [stackoverflow thread], we finally
decide to use [docker-volume-snapshot] to simplify the migration process.

1. `docker-volume-snapshot create xyz_volume xyz_volume.tar.gz` to backup
   volumes, then `scp` to new server.
1. `docker compose create` to create volumes, but not start running the
   containers.
1. `docker-volume-snapshot restore xyz_volume.tar.gz xyz_volume` to restore
   volumes.

[docker documentation]:
  https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes
[stackoverflow thread]:
  https://stackoverflow.com/questions/21597463/how-to-port-data-only-volumes-from-one-host-to-another
[docker-volume-snapshot]:
  https://github.com/junedkhatri31/docker-volume-snapshot
