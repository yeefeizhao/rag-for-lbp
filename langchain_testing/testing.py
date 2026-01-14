import os
import hashlib
import csv
import xml.etree.ElementTree as ET
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from langchain_core.runnables import chain
import shutil
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required API keys are set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not os.getenv("LANGCHAIN_API_KEY"):
    raise ValueError("LANGCHAIN_API_KEY not found in environment variables")

# Enable LangChain tracing (optional)
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")


def calculate_folder_hash(folder_path):
    hasher = hashlib.md5()
    for root, _, files in os.walk(folder_path):
        for filename in sorted(files):
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
    return hasher.hexdigest()


def load_xml(folder_path):
    documents = []
    error_count = 0
    files = 0

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' not found.")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.parse(file_path, parser=parser)
            root = tree.getroot()

            title = root.find('title').text.strip()
            url = root.find('url').text.strip()
            files += 1

            for section in root.findall('.//section'):
                section_title_elem = section.find('sectionTitle') if section.find(
                    'sectionTitle').text is not None else None
                section_content = section.find('sectionContent').text.strip()

                if section_title_elem is not None:
                    section_title = section_title_elem.text.strip()
                    if section_title != title:
                        full_title = f"{title} - {section_title}"
                    else:
                        full_title = title
                else:
                    full_title = title

                print(f"Parsing: {full_title}")
                documents.append(Document(page_content=section_content, metadata={
                                 'title': full_title, 'url': url}))

        except ET.ParseError as e:
            print(f"Error parsing {file_path}: {e}")
            error_count += 1

        except Exception as e:
            print(f"An error occurred with file {file_path}: {e}")
            error_count += 1

    print(
        f"Loaded {len(documents)} sections from {files} XML files in {folder_path}")
    print(f"Encountered {error_count} errors during processing.")

    return documents


def load_hash_from_file(hash_path):
    if os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            return f.read().strip()
    return None


def save_hash_to_file(hash_path, hash_value):
    with open(hash_path, 'w') as f:
        f.write(hash_value)


def recreate_vectorstore(directory, hash_path, vectorstore_path):
    current_hash = calculate_folder_hash(directory)
    saved_hash = load_hash_from_file(hash_path)
    if current_hash != saved_hash or saved_hash is None:
        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
        save_hash_to_file(hash_path, current_hash)
        return True
    return False


SIMILARITY_THRESHOLD = 0.4


@chain
def retriever(query: str) -> List[Document]:
    docs, scores = zip(*vectorstore.similarity_search_with_score(query, k=7))
    filtered_docs = [doc for doc, score in zip(
        docs, scores) if score <= SIMILARITY_THRESHOLD]
    for doc, score in zip(filtered_docs, scores):
        doc.metadata["score"] = score

    return filtered_docs


def retrieval_details(chain, query, rag):
    try:
        print(f"Sending query: {query}")
        response = chain.invoke(query)
        # context = retriever.invoke(query) if rag else []
        answer = response if rag else response.content

        return answer

    except Exception as e:
        print(f"An error occurred during retrieval: {e}")
        return "Error", []


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


"""def write_to_csv_with_documents(results, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Model", "Config", "Question", "Answer", "Document Title",
                        "Document URL", "Document Score", "Document Content"])
        for result in results:
            model, config, question, answer, docs = result
            for doc in docs:
                writer.writerow([
                    model,
                    config,
                    question,
                    answer,
                    doc.metadata.get('title', ''),
                    doc.metadata.get('url', ''),
                    doc.metadata.get('score', ''),
                    doc.page_content
                ])"""


def write_to_csv(results, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Model", "Question", "Answer"])
        for result in results:
            model, question, answer = result
            writer.writerow([
                model,
                question,
                answer
            ])


directory = 'data'
vectorstore_path = './chroma_db'
hash_path = './chroma_db/hash.txt'

if os.path.exists(vectorstore_path) and not recreate_vectorstore(directory, hash_path, vectorstore_path):
    vectorstore = Chroma(persist_directory=vectorstore_path,
                         embedding_function=OpenAIEmbeddings())
    print("Vectorstore loaded from disk.")
else:
    documents = load_xml(directory)
    batch_size = 100
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, strip_whitespace=True)

    all_splits = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        splits = text_splitter.split_documents(batch)
        all_splits.extend(splits)

    vectorstore = Chroma.from_documents(
        documents=all_splits,
        embedding=OpenAIEmbeddings(
            model="text-embedding-ada-002", embedding_ctx_length=1000, chunk_size=1000),
        persist_directory=vectorstore_path
    )
    print("Vectorstore created and saved to disk.")
    current_hash = calculate_folder_hash(directory)
    save_hash_to_file(hash_path, current_hash)

# removed "llama3"
"""if model == "llama3":
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not hf_token:
                raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment variables. Required for Llama3 model.")
            endpoint = HuggingFaceEndpoint(
                repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
                task="text-generation",
                top_k=50,
                temperature=0.7,
                repetition_penalty=1.03,
                huggingfacehub_api_token=hf_token,
            )
            llm = ChatHuggingFace(llm=endpoint)"""

models = ["gpt-4", "gpt-3.5-turbo-0125", "gpt-4o-mini", "gpt-4o"]
results = []

for model in models:
    try:
        print(f"Initializing ChatOpenAI with model {model}...")
        llm = ChatOpenAI(model=model, temperature=0)

        few_shot_examples = [
            {"input": "Can you explain how to lift properly to avoid excessive strain on the back?",
             "output": "**Safe Lifting Tips:**\n1. **Get Close:** Keep the item close to your body.\n2. **Bend at the Knees:** Bend your hips and knees, not your back.\n3. **Breathe:** Don't hold your breath.\n4. **Lift with Your Legs:** Use your leg muscles.\n5. **Pivot:** Move your feet, avoid twisting your back."},
            {"input": "How can a patient set up their desk ergonomically?",
             "output": "**Ergonomic Desk Setup Tips:**\n1. **Chair:** Support your back, knees level with hips, feet flat.\n2. **Desk:** Adequate space for legs and feet.\n3. **Monitor:** Arm's length away, eye level.\n4. **Keyboard and Mouse:** Wrists straight, hands below elbow level.\n5. **Movement:** Move around at least once per hour."},
        ]

        few_shot_template = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}")
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=few_shot_template,
            examples=few_shot_examples,
        )

        system_prompt = (
            "You are an assistant for physical therapists helping with lower back pain patients. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, say that you don't know. "
            "\n\n"
            "{context}"
        )

        for config in ["_RAGFS", "_RAGNFS", "_NRAG"]:
            print(f"Testing {model} with configuration: {config}")

            if config == "_RAGFS":
                qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        few_shot_prompt,
                        ("human", "{input}"),
                    ]
                )
                chain = (  # rag chain
                    {"context": retriever | format_docs,
                     "input": RunnablePassthrough()}
                    | qa_prompt
                    | llm | StrOutputParser()
                )

            elif config == "_RAGNFS":
                qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        ("human", "{input}"),
                    ]
                )

                chain = (  # rag chain
                    {"context": retriever | format_docs,
                     "input": RunnablePassthrough()}
                    | qa_prompt
                    | llm | StrOutputParser()
                )

            elif config == "_NRAG":
                chain = llm

            input_questions = [
                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 1: \nWork Status: Employed part-time\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 3 days per week\nResistance Training: 1 day per week\nExercise Makes Back Worse: Strongly disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Somewhat agree\nChiropractor/Physical Therapist Help: Somewhat disagree\nInjection Help: Strongly agree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 2: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 5 days per week\nResistance Training: 2 days per week\nExercise Makes Back Worse: Somewhat agree\nDesk Position Confidence: Strongly agree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Strongly agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 3: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 0 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Somewhat disagree\nChiropractor/Physical Therapist Help: Strongly disagree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 4: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 4 days per week\nResistance Training: 3 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Strongly disagree\nLifting Technique Confidence: Strongly agree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Strongly agree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 5: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 1 day per week\nResistance Training: 2 days per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 6: \nWork Status: Employed part-time\nDaily Activity: More time standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 7 days per week\nResistance Training: 6 days per week\nExercise Makes Back Worse: Strongly disagree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Somewhat agree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Strongly disagree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 7: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 5 days per week\nResistance Training: 1 day per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Somewhat disagree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Strongly agree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Strongly agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 8: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 2 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Somewhat agree\nDesk Position Confidence: Strongly disagree\nLifting Technique Confidence: Strongly agree\nChiropractor/Physical Therapist Help: Somewhat disagree\nInjection Help: Strongly agree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 9: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 6 days per week\nResistance Training: 4 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Strongly agree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 10: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 0 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Somewhat disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 11: \nWork Status: Employed part-time\nDaily Activity: More time standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 4 days per week\nResistance Training: 3 days per week\nExercise Makes Back Worse: Strongly disagree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Somewhat agree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 12: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 6 days per week\nResistance Training: 5 days per week\nExercise Makes Back Worse: Somewhat agree\nDesk Position Confidence: Strongly agree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 13: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 3 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 14: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 7 days per week\nResistance Training: 7 days per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Somewhat disagree\nInjection Help: Strongly agree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Strongly agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 15: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 2 days per week\nResistance Training: 2 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 16: \nWork Status: Employed part-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 1 day per week\nResistance Training: 1 day per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Strongly disagree\nLifting Technique Confidence: Strongly agree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Strongly disagree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 17: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 5 days per week\nResistance Training: 3 days per week\nExercise Makes Back Worse: Strongly disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Somewhat agree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 18: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 2 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Strongly disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 19: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 4 days per week\nResistance Training: 4 days per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Strongly agree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Somewhat disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 20: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 0 days per week\nResistance Training: 1 day per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Somewhat agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 21: \nWork Status: Employed part-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 3 days per week\nResistance Training: 3 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Somewhat disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Strongly agree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 22: \nWork Status: Employed full-time\nDaily Activity: More time standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 7 days per week\nResistance Training: 7 days per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Strongly disagree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Strongly disagree\nRest When Painful: Somewhat disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 23: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 4 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Strongly agree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 24: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 6 days per week\nResistance Training: 3 days per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Strongly disagree\nLifting Technique Confidence: Somewhat agree\nChiropractor/Physical Therapist Help: Somewhat disagree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Strongly disagree\nRest When Painful: Somewhat agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 25: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 1 day per week\nResistance Training: 1 day per week\nExercise Makes Back Worse: Neither agree nor disagree\nDesk Position Confidence: Somewhat disagree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Strongly agree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 26: \nWork Status: Employed part-time\nDaily Activity: More time standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 2 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Somewhat agree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 27: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 5 days per week\nResistance Training: 2 days per week\nExercise Makes Back Worse: Strongly disagree\nDesk Position Confidence: Somewhat agree\nLifting Technique Confidence: Neither agree nor disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Neither agree nor disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 28: \nWork Status: Unemployed but seeking work\nDaily Activity: More time standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 3 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Neither agree nor disagree\nLifting Technique Confidence: Somewhat disagree\nChiropractor/Physical Therapist Help: Neither agree nor disagree\nInjection Help: Strongly disagree\nX-rays/MRIs Needed: Somewhat agree\nRest When Painful: Strongly agree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 29: \nWork Status: Employed full-time\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: Yes\nAerobic Activity: 4 days per week\nResistance Training: 2 days per week\nExercise Makes Back Worse: Somewhat disagree\nDesk Position Confidence: Strongly agree\nLifting Technique Confidence: Somewhat disagree\nChiropractor/Physical Therapist Help: Strongly agree\nInjection Help: Somewhat disagree\nX-rays/MRIs Needed: Neither agree nor disagree\nRest When Painful: Strongly disagree",

                "Please create patient education materials written at a 6th grade level Flesch-Kincaid Grade Level for Patient 30: \nWork Status: Do not work outside the home and not seeking to\nDaily Activity: More time sitting than standing/walking/moving around\nLifts Objects: No\nAerobic Activity: 2 days per week\nResistance Training: 0 days per week\nExercise Makes Back Worse: Strongly agree\nDesk Position Confidence: Strongly disagree\nLifting Technique Confidence: Strongly disagree\nChiropractor/Physical Therapist Help: Somewhat disagree\nInjection Help: Neither agree nor disagree\nX-rays/MRIs Needed: Somewhat disagree\nRest When Painful: Neither agree nor disagree"
            ]

            print(f"Processing questions for model {model}, {config}...")
            for input_question in input_questions:
                try:

                    answer = retrieval_details(
                        chain, input_question, config != "_NRAG")
                    print(f"Human: {input_question[:41]}")
                    print(f"Assistant: {answer}")
                    
                    model_config = model.upper() + config
                    results.append(
                        (model_config, input_question, answer))
                except Exception as e:
                    print(
                        f"An error occurred during question processing for model {model}: {e}")
    except Exception as e:
        print(f"An error occurred while processing model {model}: {e}")


# write_to_csv_with_documents(results, "results_output_with_documents.csv")
write_to_csv(results, "education_materials_test.csv")

print(f"Results saved to csv")
