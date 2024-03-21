import { getRAGTemplate } from '$lib/apis/rag';

export const RAGTemplate = async (token: string, context: string, query: string) => {
	let template = await getRAGTemplate(token).catch(() => {
		return `Use the following context as your learned knowledge, inside <context></context> XML tags.
		<context>
		  [context]
		</context>
		
		Given the context information, answer the query.
		Query: [query]`;
	});

	template = template.replace(/\[context\]/g, context);
	template = template.replace(/\[query\]/g, query);

	return template;
};
