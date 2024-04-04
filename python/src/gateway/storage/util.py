import pika, json

def upload(f, fs, channel, access):
    try:
        # assign file ID object returned by mongodb to a variable
        fid = fs.put(f)
    except Exception as err:
        print(err)
        return "internal server error: failed to put file in database", 500
    
    # this is the message to put onto the queue
    message = {
        # convert ID object into a string
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    # try to put message on our rabbitmq queue
    try:
        channel.basic_publish(
            # set exchange to default: every queue that is created is automatically bound to the exchange with a routing key same as the queue name. 
            exchange="",
            # tells rabbitmq which queue to send messages to with a routing key.
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                # tells rabbitmq that this message should be persisted in the event of a pod crash or restart
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    
    # delete file from mongodb if putting message in queue is unsuccessful
    except Exception as err:
        print(err)
        fs.delete(fid)
        return "internal server error", 500
