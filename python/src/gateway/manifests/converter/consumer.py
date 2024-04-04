import pika, sys, os, time
from pymongo import MongoClient
import gridfs
# package to create
from convert import to_mp3

def main():
    client = MongoClient("host.minikube.internal", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    #rabbitmq connection
    # Internally, when the pika library attempts to establish a connection to RabbitMQ using the specified hostname, it relies on the operating system's DNS resolution mechanisms.
    # In a Kubernetes environment, the DNS resolution for service names like "rabbitmq" is managed by Kubernetes itself, ensuring that the hostname is resolved to the correct IP address of the RabbitMQ service within the cluster.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        # function in our to_mp3 module named .start()
        err = to_mp3.start()
        if err:
            # nack = negative acknowledgement, message will not be removed from queue
            # delivery tag uniquely identifies the delivery on a channel (like a ID number), lets rabbitmq know to not remove that message from the queue
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # on_message_callback is a parameter used in RabbitMQ consumer methods to specify the function that should be called when a message is received. This function will be invoked for each message that the consumer receives from the queue. 
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
