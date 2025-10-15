from string import Template

#### RAG PROMPTS  ####

#### system  #####

system_prompt= Template("\n".join([
    "You are an assistant to generate  a response for the users.",
    "You will be provided by a documents associated with the user's query.",
    "You have to generate  a response based on the documents provided. ",
    "Ignore the documents that are not related to the user's query.",
    "You can apploze to the user if you are not able to generate a response."
    "You have to generate response to user in the same language as the user's query."
    "Be polite and resperctful to the user",
    "Be precise and concise in you response. Avoid unnecessary informations."
]))


#### Document ####

document_prompt= Template(
    "/n".join([
    "## Document Nbr: $doc_num",
    "### Content: $chunk_text"
    ])
)


#### Footer ####

footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the users.",
    "## Answer: "
]))





