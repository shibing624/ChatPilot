<script lang="ts">
	import { getVersionUpdates } from '$lib/apis';
	import { getOllamaVersion } from '$lib/apis/ollama';
	import { WEBUI_VERSION } from '$lib/constants';
	import { WEBUI_NAME, config, showChangelog } from '$lib/stores';
	import { compareVersion } from '$lib/utils';
	import { onMount } from 'svelte';

	let ollamaVersion = '';

	let updateAvailable = null;
	let version = {
		current: '',
		latest: ''
	};

	const checkForVersionUpdates = async () => {
		updateAvailable = null;
		version = await getVersionUpdates(localStorage.token).catch((error) => {
			return {
				current: WEBUI_VERSION,
				latest: WEBUI_VERSION
			};
		});

		console.log(version);

		updateAvailable = compareVersion(version.latest, version.current);
		console.log(updateAvailable);
	};

	onMount(async () => {
		ollamaVersion = await getOllamaVersion(localStorage.token).catch((error) => {
			return '';
		});

		checkForVersionUpdates();
	});
</script>

<div class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
	<div class=" space-y-3">
		<div>
			<div class=" mb-2.5 text-sm font-medium flex space-x-2 items-center">
				<div>
					{$WEBUI_NAME} Version
				</div>
			</div>
			<div class="flex w-full justify-between items-center">
				<div class="flex flex-col text-xs text-gray-700 dark:text-gray-200">
					<div>
						v{WEBUI_VERSION}
					</div>
				</div>

			</div>
		</div>

		{#if ollamaVersion}
			<hr class=" dark:border-gray-700" />

			<div>
				<div class=" mb-2.5 text-sm font-medium">Ollama Version</div>
				<div class="flex w-full">
					<div class="flex-1 text-xs text-gray-700 dark:text-gray-200">
						{ollamaVersion ?? 'N/A'}
					</div>
				</div>
			</div>
		{/if}

		<hr class=" dark:border-gray-700" />

		<div class="flex space-x-1">

			<a href="https://github.com/shibing624/ChatPilot" target="_blank">
				<img
					alt="Github Repo"
					src="https://img.shields.io/github/stars/shibing624/ChatPilot?style=social&label=Star us on Github"
				/>
			</a>
		</div>

		<div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
			Created by <a
				class=" text-gray-500 dark:text-gray-300 font-medium"
				href="https://github.com/shibing624"
				target="_blank">shibing624</a
			>
		</div>
	</div>
</div>
