import httpx

from .device_client_constants import ClientConstants
import requests
from fastapi.responses import Response
from fastapi.responses import StreamingResponse


class FedMLHttpInference:
    def __init__(self):
        pass

    @staticmethod
    def run_http_inference_with_curl_request(
            inference_url, inference_input_list, inference_output_list,
            inference_type="default", engine_type="default", timeout=None
    ):
        model_inference_result = {}
        if inference_type == "default":
            model_api_headers = {'Content-Type': 'application/json', 'Connection': 'close',
                                 'Accept': 'application/json'}
        else:
            model_api_headers = {'Content-Type': 'application/json', 'Connection': 'close',
                                 'Accept': inference_type}
        if engine_type == "default":
            model_inference_json = inference_input_list
        else:  # triton
            model_inference_json = {
                "inputs": inference_input_list,
                "outputs": inference_output_list
            }

        response_ok = False
        try:
            if model_inference_json.get("stream", False):
                model_inference_result = StreamingResponse(
                    stream_generator(inference_url, input_json=model_inference_json),
                    media_type="text/event-stream")
                response_ok = True
            else:
                if timeout is None:
                    response = requests.post(inference_url, headers=model_api_headers, json=model_inference_json)
                else:
                    response = requests.post(
                        inference_url, headers=model_api_headers, json=model_inference_json, timeout=timeout)
                if response.status_code == 200:
                    response_ok = True
                    if inference_type == "default":
                        model_inference_result = response.json()
                    elif inference_type == "image/png":
                        binary_content: bytes = response.content
                        model_inference_result = Response(content=binary_content, media_type="image/png")
                    else:
                        model_inference_result = response.json()
        except Exception as e:
            # print("Error in running inference: {}".format(e))
            pass

        return response_ok, model_inference_result


async def stream_generator(inference_url, input_json):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", inference_url, json=input_json,
                                 timeout=ClientConstants.WORKER_STREAM_API_TIMEOUT) as response:
            async for chunk in response.aiter_lines():
                yield chunk
