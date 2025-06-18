<script lang="ts">
	import { v4 as uuidv4 } from 'uuid';

	import { chats, config, modelfiles, settings, user } from '$lib/stores';
	import { tick } from 'svelte';

	import { toast } from 'svelte-sonner';
	import { getChatList, updateChatById } from '$lib/apis/chats';

	import UserMessage from './Messages/UserMessage.svelte';
	import ResponseMessage from './Messages/ResponseMessage.svelte';
	import Placeholder from './Messages/Placeholder.svelte';
	import Spinner from '../common/Spinner.svelte';
	import { imageGenerations } from '$lib/apis/images';

	export let chatId = '';
	export let sendPrompt: Function;
	export let continueGeneration: Function;
	export let regenerateResponse: Function;

	export let processing = '';
	export let bottomPadding = false;
	export let autoScroll;
	export let selectedModels;
	export let history = {};
	export let messages = [];

	export let selectedModelfiles = [];

	let messagesContainer;
	const SCROLL_OFFSET = 120;

	// 改进的滚动函数
	function smoothScrollToMessage(element, immediate = false) {
		if (!element) return;
		
		const headerHeight = 60;
		const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - headerHeight - SCROLL_OFFSET;
		
		window.scrollTo({
			top: Math.max(0, targetPosition),
			behavior: immediate ? 'auto' : 'smooth'
		});
	}

	// 监听消息变化
	$: if (messages) {
		tick().then(() => {
			const latestMessage = document.querySelector('.message-' + messages[messages.length - 1]?.id);
			if (latestMessage) {
				const isUserMessage = messages[messages.length - 1]?.role === 'user';
				// 如果是用户消息，立即滚动到顶部
				if (isUserMessage) {
					window.scrollTo({ top: 0, behavior: 'auto' });
				} else {
					// 如果是模型回答，平滑滚动到消息位置
					smoothScrollToMessage(latestMessage);
				}
			}
		});
	}

	// 监听新消息添加
	let previousMessagesLength = 0;
	$: if (messages.length > previousMessagesLength) {
		previousMessagesLength = messages.length;
		tick().then(() => {
			const latestMessage = document.querySelector('.message-' + messages[messages.length - 1]?.id);
			if (latestMessage) {
				const isUserMessage = messages[messages.length - 1]?.role === 'user';
				// 如果是用户消息，立即滚动到顶部
				if (isUserMessage) {
					window.scrollTo({ top: 0, behavior: 'auto' });
				} else {
					// 如果是模型回答，平滑滚动到消息位置
					smoothScrollToMessage(latestMessage);
				}
			}
		});
	}

	const scrollToBottom = () => {
		const element = document.getElementById('messages-container');
		if (element) {
			element.scrollTop = element.scrollHeight;
		}
	};

	const copyToClipboard = (text) => {
		if (!navigator.clipboard) {
			var textArea = document.createElement('textarea');
			textArea.value = text;

			// Avoid scrolling to bottom
			textArea.style.top = '0';
			textArea.style.left = '0';
			textArea.style.position = 'fixed';

			document.body.appendChild(textArea);
			textArea.focus();
			textArea.select();

			try {
				var successful = document.execCommand('copy');
				var msg = successful ? 'successful' : 'unsuccessful';
				console.log('Fallback: Copying text command was ' + msg);
			} catch (err) {
				console.error('Fallback: Oops, unable to copy', err);
			}

			document.body.removeChild(textArea);
			return;
		}
		navigator.clipboard.writeText(text).then(
			function () {
				console.log('Async: Copying to clipboard was successful!');
				toast.success('Copying to clipboard was successful!');
			},
			function (err) {
				console.error('Async: Could not copy text: ', err);
			}
		);
	};

	const confirmEditMessage = async (messageId, content) => {
		let userPrompt = content;
		let userMessageId = uuidv4();

		let userMessage = {
			id: userMessageId,
			parentId: history.messages[messageId].parentId,
			childrenIds: [],
			role: 'user',
			content: userPrompt,
			...(history.messages[messageId].files && { files: history.messages[messageId].files })
		};

		let messageParentId = history.messages[messageId].parentId;

		if (messageParentId !== null) {
			history.messages[messageParentId].childrenIds = [
				...history.messages[messageParentId].childrenIds,
				userMessageId
			];
		}

		history.messages[userMessageId] = userMessage;
		history.currentId = userMessageId;

		await tick();
		await sendPrompt(userPrompt, userMessageId, chatId);
	};

	const confirmEditResponseMessage = async (messageId, content) => {
		history.messages[messageId].originalContent = history.messages[messageId].content;
		history.messages[messageId].content = content;

		await tick();

		await updateChatById(localStorage.token, chatId, {
			messages: messages,
			history: history
		});

		await chats.set(await getChatList(localStorage.token));
	};

	const rateMessage = async (messageId, rating) => {
		history.messages[messageId].rating = rating;
		await tick();
		await updateChatById(localStorage.token, chatId, {
			messages: messages,
			history: history
		});

		await chats.set(await getChatList(localStorage.token));
	};

	const showPreviousMessage = async (message) => {
		if (message.parentId !== null) {
			let messageId =
				history.messages[message.parentId].childrenIds[
					Math.max(history.messages[message.parentId].childrenIds.indexOf(message.id) - 1, 0)
				];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		} else {
			let childrenIds = Object.values(history.messages)
				.filter((message) => message.parentId === null)
				.map((message) => message.id);
			let messageId = childrenIds[Math.max(childrenIds.indexOf(message.id) - 1, 0)];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		}

		await tick();

		const element = document.getElementById('messages-container');
		autoScroll = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

		setTimeout(() => {
			scrollToBottom();
		}, 100);
	};

	const showNextMessage = async (message) => {
		if (message.parentId !== null) {
			let messageId =
				history.messages[message.parentId].childrenIds[
					Math.min(
						history.messages[message.parentId].childrenIds.indexOf(message.id) + 1,
						history.messages[message.parentId].childrenIds.length - 1
					)
				];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		} else {
			let childrenIds = Object.values(history.messages)
				.filter((message) => message.parentId === null)
				.map((message) => message.id);
			let messageId =
				childrenIds[Math.min(childrenIds.indexOf(message.id) + 1, childrenIds.length - 1)];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		}

		await tick();

		const element = document.getElementById('messages-container');
		autoScroll = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

		setTimeout(() => {
			scrollToBottom();
		}, 100);
	};

	const messageDeleteHandler = async (messageId) => {
		const messageToDelete = history.messages[messageId];
		const messageParentId = messageToDelete.parentId;
		const messageChildrenIds = messageToDelete.childrenIds ?? [];
		const hasSibling = messageChildrenIds.some(
			(childId) => history.messages[childId]?.childrenIds?.length > 0
		);
		messageChildrenIds.forEach((childId) => {
			const child = history.messages[childId];
			if (child && child.childrenIds) {
				if (child.childrenIds.length === 0 && !hasSibling) {
					// if last prompt/response pair
					history.messages[messageParentId].childrenIds = [];
					history.currentId = messageParentId;
				} else {
					child.childrenIds.forEach((grandChildId) => {
						if (history.messages[grandChildId]) {
							history.messages[grandChildId].parentId = messageParentId;
							history.messages[messageParentId].childrenIds.push(grandChildId);
						}
					});
				}
			}
			// remove response
			history.messages[messageParentId].childrenIds = history.messages[
				messageParentId
			].childrenIds.filter((id) => id !== childId);
		});
		// remove prompt
		history.messages[messageParentId].childrenIds = history.messages[
			messageParentId
		].childrenIds.filter((id) => id !== messageId);
		await updateChatById(localStorage.token, chatId, {
			messages: messages,
			history: history
		});
	};

	// const messageDeleteHandler = async (messageId) => {
	// 	const message = history.messages[messageId];
	// 	const parentId = message.parentId;
	// 	const childrenIds = message.childrenIds ?? [];
	// 	const grandchildrenIds = [];

	// 	// Iterate through childrenIds to find grandchildrenIds
	// 	for (const childId of childrenIds) {
	// 		const childMessage = history.messages[childId];
	// 		const grandChildrenIds = childMessage.childrenIds ?? [];

	// 		for (const grandchildId of grandchildrenIds) {
	// 			const childMessage = history.messages[grandchildId];
	// 			childMessage.parentId = parentId;
	// 		}
	// 		grandchildrenIds.push(...grandChildrenIds);
	// 	}

	// 	history.messages[parentId].childrenIds.push(...grandchildrenIds);
	// 	history.messages[parentId].childrenIds = history.messages[parentId].childrenIds.filter(
	// 		(id) => id !== messageId
	// 	);

	// 	// Select latest message
	// 	let currentMessageId = grandchildrenIds.at(-1);
	// 	if (currentMessageId) {
	// 		let messageChildrenIds = history.messages[currentMessageId].childrenIds;
	// 		while (messageChildrenIds.length !== 0) {
	// 			currentMessageId = messageChildrenIds.at(-1);
	// 			messageChildrenIds = history.messages[currentMessageId].childrenIds;
	// 		}
	// 		history.currentId = currentMessageId;
	// 	}

	// 	await updateChatById(localStorage.token, chatId, { messages, history });
	// };
</script>

{#if messages.length == 0}
	<Placeholder models={selectedModels} modelfiles={selectedModelfiles} />
{:else}
	<div class=" pb-10">
		{#key chatId}
			{#each messages as message, messageIdx}
				<div class=" w-full">
					<div
						class="flex flex-col justify-between px-5 mb-3 {$settings?.fullScreenMode ?? null
							? 'max-w-full'
							: 'max-w-3xl'} mx-auto rounded-lg group"
					>
						{#if message.role === 'user'}
							<UserMessage
								on:delete={() => messageDeleteHandler(message.id)}
								user={$user}
								{message}
								isFirstMessage={messageIdx === 0}
								siblings={message.parentId !== null
									? history.messages[message.parentId]?.childrenIds ?? []
									: Object.values(history.messages)
											.filter((message) => message.parentId === null)
											.map((message) => message.id) ?? []}
								{confirmEditMessage}
								{showPreviousMessage}
								{showNextMessage}
								{copyToClipboard}
							/>
						{:else}
							<ResponseMessage
								{message}
								modelfiles={selectedModelfiles}
								siblings={history.messages[message.parentId]?.childrenIds ?? []}
								isLastMessage={messageIdx + 1 === messages.length}
								{confirmEditResponseMessage}
								{showPreviousMessage}
								{showNextMessage}
								{rateMessage}
								{copyToClipboard}
								{continueGeneration}
								{regenerateResponse}
								on:save={async (e) => {
									console.log('save', e);

									const message = e.detail;
									history.messages[message.id] = message;
									await updateChatById(localStorage.token, chatId, {
										messages: messages,
										history: history
									});
								}}
							/>
						{/if}
					</div>
				</div>
			{/each}

			{#if bottomPadding}
				<div class=" mb-10" />
			{/if}
		{/key}
	</div>
{/if}
