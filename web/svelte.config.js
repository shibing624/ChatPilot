import adapter from '@sveltejs/adapter-static';
import sveltePreprocess from 'svelte-preprocess';

const config = {
  preprocess: sveltePreprocess({
    typescript: true,
  }),

  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html'
    })
  }
};

export default config;