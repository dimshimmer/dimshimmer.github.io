<script lang="ts">
import {
	layoutWithLines,
	prepareWithSegments,
	type LayoutLine,
	type PreparedTextWithSegments,
} from "@chenglou/pretext";
import { onMount } from "svelte";

export let text: string;

let root: HTMLDivElement;
let lines: LayoutLine[] = [];
let height = 0;
let lineHeight = 0;
let prepared: PreparedTextWithSegments | null = null;
let preparedFont = "";
let observer: ResizeObserver | null = null;
let animationFrame = 0;

const makeFont = (style: CSSStyleDeclaration): string =>
	[
		style.fontStyle,
		style.fontVariant,
		style.fontWeight,
		style.fontSize,
		style.fontFamily,
	].join(" ");

const refreshLayout = (): void => {
	if (!root) return;

	const width = Math.floor(root.clientWidth);
	if (width <= 0) return;

	const style = getComputedStyle(root);
	const nextFont = makeFont(style);
	const nextLineHeight = Number.parseFloat(style.lineHeight);
	if (!Number.isFinite(nextLineHeight)) return;

	if (prepared === null || preparedFont !== nextFont) {
		prepared = prepareWithSegments(text, nextFont, { wordBreak: "keep-all" });
		preparedFont = nextFont;
	}

	const result = layoutWithLines(prepared, width, nextLineHeight);
	lines = result.lines;
	height = result.height;
	lineHeight = nextLineHeight;
};

const scheduleRefresh = (): void => {
	if (animationFrame !== 0) return;

	animationFrame = requestAnimationFrame(() => {
		animationFrame = 0;
		refreshLayout();
	});
};

onMount(() => {
	const start = async (): Promise<void> => {
		await document.fonts?.ready;
		refreshLayout();

		observer = new ResizeObserver(scheduleRefresh);
		observer.observe(root);
	};

	start();

	return () => {
		observer?.disconnect();
		if (animationFrame !== 0) cancelAnimationFrame(animationFrame);
	};
});
</script>

<div bind:this={root} class="pretext-intro" aria-label={text}>
	{#if lines.length === 0}
		<p>{text}</p>
	{:else}
		<p class="sr-only">{text}</p>
		<div class="line-stage" style={`height: ${height}px`} aria-hidden="true">
			{#each lines as line, index}
				<span
					class="line"
					style={`top: ${index * lineHeight}px; width: ${Math.ceil(line.width)}px`}
				>
					{line.text}
				</span>
			{/each}
		</div>
	{/if}
</div>

<style>
.pretext-intro {
	color: rgb(23 23 23 / 0.72);
	font-family: Roboto, Arial, sans-serif;
	font-size: 1.05rem;
	font-weight: 500;
	letter-spacing: 0;
	line-height: 1.75;
}

:global(.dark) .pretext-intro {
	color: rgb(255 255 255 / 0.72);
}

.pretext-intro p {
	margin: 0;
}

.line-stage {
	position: relative;
	width: 100%;
}

.line {
	left: 0;
	position: absolute;
	white-space: pre;
}
</style>
