import * as onnx from 'https://cdn.jsdelivr.net/npm/onnxjs@1.0.0/dist/onnx.js';


const session = new onnx.InferenceSession();
console.log("LOADING")
await session.loadModel("https://huggingface.co/Xenova/detr-resnet-50/blob/main/onnx/model.onnx");
console.log("DONE")