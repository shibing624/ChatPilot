<script lang="ts">
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { getChatById } from '$lib/apis/chats';
	import { WEBUI_NAME, chatId, modelfiles, settings } from '$lib/stores';
	import ShareChatModal from '../chat/ShareChatModal.svelte';
	import TagInput from '../common/Tags/TagInput.svelte';
	import Tags from '../common/Tags.svelte';

	export let initNewChat: Function;
	export let title: string = $WEBUI_NAME;
	export let shareEnabled: boolean = false;

	export let tags = [];
	export let addTag: Function;
	export let deleteTag: Function;

	let showShareChatModal = false;

	let tagName = '';
	let showTagInput = false;

	const shareChat = async () => {
		const chat = (await getChatById(localStorage.token, $chatId)).chat;
		console.log('share', chat);

		toast.success('Redirecting you to OpenWebUI Community');
		const url = 'https://openwebui.com';
		// const url = 'http://localhost:5173';

		const tab = await window.open(`${url}/chats/upload`, '_blank');
		window.addEventListener(
			'message',
			(event) => {
				if (event.origin !== url) return;
				if (event.data === 'loaded') {
					tab.postMessage(
						JSON.stringify({
							chat: chat,
							modelfiles: $modelfiles.filter((modelfile) => chat.models.includes(modelfile.tagName))
						}),
						'*'
					);
				}
			},
			false
		);
	};

	const downloadChat = async () => {
		const chat = (await getChatById(localStorage.token, $chatId)).chat;
		console.log('download', chat);

		const chatText = chat.messages.reduce((a, message, i, arr) => {
			return `${a}### ${message.role.toUpperCase()}\n${message.content}\n\n`;
		}, '');

		let blob = new Blob([chatText], {
			type: 'text/plain'
		});

		saveAs(blob, `chat-${chat.title}.txt`);
	};
</script>

<ShareChatModal bind:show={showShareChatModal} {downloadChat} {shareChat} />
<nav
	id="nav"
	class=" sticky py-2.5 top-0 flex flex-row justify-center bg-white/95 dark:bg-gray-900/90 dark:text-gray-200 backdrop-blur-xl z-30"
>
	<div
		class=" flex {$settings?.fullScreenMode ?? null
			? 'max-w-full'
			: 'max-w-3xl'}  w-full mx-auto px-3"
	>
		<div class="flex items-center w-full max-w-full">
			<div class="pr-2 self-start">
				<button
					id="new-chat-button"
					class=" cursor-pointer p-1.5 flex dark:hover:bg-gray-700 rounded-lg transition"
					on:click={initNewChat}
				>
					<div class=" m-auto self-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 1020 1020"
							fill="currentColor"
							class="w-5 h-5"
						>
							<path
								d="M935.262724 0H88.737276C39.790922 0 0 39.43879 0 88.385144v610.596974c0 48.594223 39.790922 88.385144 88.737276 88.385145h180.995874l-11.97249 236.632737 378.541953-236.632737h298.960111c48.946355 0 88.737276-39.790922 88.737276-88.385145V88.385144c0-48.946355-39.790922-88.385144-88.737276-88.385144z m-209.870702 454.954608h-156.34663v156.698762h-114.090784v-156.698762H298.607978V341.215956h156.34663V184.869326h114.090784v156.34663h156.34663v113.738652zM156.34663 85.215956h711.30674c39.086657 0 71.130674 31.691884 71.130674 71.130674v469.392022c0 39.43879-32.044017 71.130674-71.130674 71.130674h-268.676754l-243.323246 156.34663 7.042641-156.34663H156.34663c-39.086657 0-71.130674-31.691884-71.130674-71.130674V156.34663c0-39.43879 32.044017-71.130674 71.130674-71.130674z"
							/>
						</svg>
					</div>
				</button>
			</div>
			<div class=" flex-1 self-center font-medium line-clamp-1">
				<div>
					{title != '' ? title : $WEBUI_NAME}
				</div>
			</div>

			<div class="pl-2 self-center flex items-center space-x-2">
				{#if shareEnabled}
					<Tags {tags} {deleteTag} {addTag} />

					<button
						class=" cursor-pointer p-1.5 flex dark:hover:bg-gray-700 rounded-lg transition border dark:border-gray-600"
						on:click={async () => {
							showShareChatModal = !showShareChatModal;

							// console.log(showShareChatModal);
						}}
					>
						<div class=" m-auto self-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								class="w-4 h-4"
							>
								<path
									fill-rule="evenodd"
									d="M15.75 4.5a3 3 0 1 1 .825 2.066l-8.421 4.679a3.002 3.002 0 0 1 0 1.51l8.421 4.679a3 3 0 1 1-.729 1.31l-8.421-4.678a3 3 0 1 1 0-4.132l8.421-4.679a3 3 0 0 1-.096-.755Z"
									clip-rule="evenodd"
								/>
							</svg>
						</div>
					</button>
				{/if}
			</div>
		</div>
	</div>
</nav>
