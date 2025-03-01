import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.6.0';

async function analyzeOutput(input) {
    const classifier = await pipeline('text-classification', 'Titeiiko/OTIS-Official-Spam-Model');
    const result = await classifier(input);
    
    const x = result[0];
    if (x.label === 'LABEL_0') {
        return { type: 'Not Spam', probability: x.score };
    } else {
        return { type: 'Spam', probability: x.score };
    }
}

analyzeOutput("Cһeck out our amazinɡ bооѕting serviсe ѡhere you can get to Leveӏ 3 for 3 montһs for just 20 USD.")
    .then(result => console.log(result));
