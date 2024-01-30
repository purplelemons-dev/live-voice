from typing import MutableSequence
from http_plus_purplelemons_dev import Server, Request, StreamResponse, Response
from google.cloud import speech_v2 as speech
from queue import Queue
from threading import Thread
import time


project_id = "fabled-alchemy-324023"
server = Server()
queue: Queue[bytes] = Queue()
stream_queue: Queue[MutableSequence[speech.StreamingRecognitionResult]] = Queue()


@server.post("/audiostream")
def _(req: Request, res: Response):
    queue.put(req.body)
    return res.set_body("OK")


@server.stream("/stream")
def _(req: Request, res: StreamResponse):
    try:
        for result in get_stream():
            if result:
                yield res.event(result.alternatives[0].transcript + " ")
    except Exception as e:
        print(e)
        return res.status(500)


def get_stream():
    while True:
        yield from stream_queue.get()


def main():
    client = speech.SpeechClient()
    print("#" * 86)
    return client


if __name__ == "__main__":
    t = Thread(target=server.listen, args=(9988,))
    t.start()

    recognition_config = speech.RecognitionConfig(
        auto_decoding_config=speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
        adaptation=speech.SpeechAdaptation(
            phrase_sets=[
                speech.SpeechAdaptation.AdaptationPhraseSet(
                    phrase_set="projects/122210675403/locations/global/phraseSets/customphrase"
                )
            ]
        ),
    )
    streaming_config = speech.StreamingRecognitionConfig(config=recognition_config)

    client = main()

    def requests(q: Queue):
        yield speech.StreamingRecognizeRequest(
            recognizer=f"projects/{project_id}/locations/global/recognizers/_",
            streaming_config=streaming_config,
        )
        while True:
            item: bytes = q.get()
            # yield streaming_config
            yield speech.StreamingRecognizeRequest(
                recognizer=f"projects/{project_id}/locations/global/recognizers/_",
                audio=item,
            )

    while True:
        try:
            for recognize in client.streaming_recognize(requests=requests(queue)):
                stream_queue.put(recognize.results)
        except Exception as e:
            print(e)
            time.sleep(1)
            client = main()
        except KeyboardInterrupt:
            break
