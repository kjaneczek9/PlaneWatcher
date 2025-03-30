run:
	sudo docker compose up --build -d
stop:
	sudo docker compose down
restart:
	sudo docker compose down
	sudo docker compose up --build -d