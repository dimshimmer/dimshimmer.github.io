<script lang="ts">
import {
	layoutNextLine,
	prepareWithSegments,
	type LayoutCursor,
	type PreparedTextWithSegments,
} from "@chenglou/pretext";
import { onMount } from "svelte";

type PositionedLine = {
	x: number;
	y: number;
	text: string;
	width: number;
};

const copy =
	"Pretext can measure and lay out multilingual text without asking the DOM for every line. This demo prepares the paragraph once, then recomputes line breaks as the available width changes. The highlighted block is treated as an obstacle, so each affected row receives a narrower text slot. 中文、English, and symbols stay in one measured stream.";

let stage: HTMLDivElement;
let lines: PositionedLine[] = [];
let prepared: PreparedTextWithSegments | null = null;
let preparedFont = "";
let lineHeight = 28;
let stageHeight = 0;
let obstacleSide: "right" | "left" = "right";
let observer: ResizeObserver | null = null;
let animationFrame = 0;

const obstacle = {
	top: 76,
	width: 196,
	height: 132,
	gap: 22,
};

const makeFont = (style: CSSStyleDeclaration): string =>
	[
		style.fontStyle,
		style.fontVariant,
		style.fontWeight,
		style.fontSize,
		style.fontFamily,
	].join(" ");

const toggleObstacle = (): void => {
	obstacleSide = obstacleSide === "right" ? "left" : "right";
	scheduleLayout();
};

const getObstacleLeft = (containerWidth: number): number =>
	obstacleSide === "right"
		? Math.max(0, containerWidth - obstacle.width)
		: 0;

const layoutDemo = (): void => {
	if (!stage) return;

	const containerWidth = Math.floor(stage.clientWidth);
	if (containerWidth <= 0) return;

	const style = getComputedStyle(stage);
	const font = makeFont(style);
	const nextLineHeight = Number.parseFloat(style.lineHeight);
	if (!Number.isFinite(nextLineHeight)) return;

	if (prepared === null || preparedFont !== font) {
		prepared = prepareWithSegments(copy, font, { wordBreak: "keep-all" });
		preparedFont = font;
	}

	lineHeight = nextLineHeight;

	const nextLines: PositionedLine[] = [];
	const cursor: LayoutCursor = { segmentIndex: 0, graphemeIndex: 0 };
	let y = 0;

	while (true) {
		const lineTop = y;
		const lineBottom = y + lineHeight;
		const intersectsObstacle =
			lineBottom > obstacle.top && lineTop < obstacle.top + obstacle.height;

		const obstacleLeft = getObstacleLeft(containerWidth);
		const x =
			intersectsObstacle && obstacleSide === "left"
				? obstacle.width + obstacle.gap
				: 0;
		const maxWidth =
			intersectsObstacle
				? Math.max(96, containerWidth - obstacle.width - obstacle.gap)
				: containerWidth;

		const line = layoutNextLine(prepared, cursor, maxWidth);
		if (line === null) break;

		nextLines.push({
			x,
			y,
			text: line.text,
			width: line.width,
		});

		cursor.segmentIndex = line.end.segmentIndex;
		cursor.graphemeIndex = line.end.graphemeIndex;
		y += lineHeight;

		if (y > 520) break;
		if (intersectsObstacle && obstacleSide === "right") {
			void obstacleLeft;
		}
	}

	lines = nextLines;
	stageHeight = Math.max(y, obstacle.top + obstacle.height);
};

const scheduleLayout = (): void => {
	if (animationFrame !== 0) return;

	animationFrame = requestAnimationFrame(() => {
		animationFrame = 0;
		layoutDemo();
	});
};

onMount(() => {
	const start = async (): Promise<void> => {
		await document.fonts?.ready;
		layoutDemo();

		observer = new ResizeObserver(scheduleLayout);
		observer.observe(stage);
	};

	start();

	return () => {
		observer?.disconnect();
		if (animationFrame !== 0) cancelAnimationFrame(animationFrame);
	};
});
</script>

<section class="demo-shell">
	<div class="toolbar">
		<div>
			<h1>Pretext Flow Demo</h1>
			<p>Manual line layout with a live obstacle.</p>
		</div>
		<button type="button" class="btn-regular toggle" on:click={toggleObstacle}>
			Move obstacle
		</button>
	</div>

	<div
		bind:this={stage}
		class="stage"
		style={`height: ${stageHeight}px`}
		aria-label={copy}
	>
		<p class="sr-only">{copy}</p>
		<div
			class="obstacle"
			class:left={obstacleSide === "left"}
			style={`top: ${obstacle.top}px; width: ${obstacle.width}px; height: ${obstacle.height}px`}
			aria-hidden="true"
		>
			<span>measured obstacle</span>
		</div>

		{#each lines as line}
			<span
				class="line"
				style={`transform: translate(${line.x}px, ${line.y}px); width: ${Math.ceil(line.width)}px`}
				aria-hidden="true"
			>
				{line.text}
			</span>
		{/each}
	</div>
</section>

<style>
.demo-shell {
	background: var(--card-bg);
	border-radius: var(--radius-large);
	padding: 1.5rem;
}

.toolbar {
	align-items: center;
	display: flex;
	gap: 1rem;
	justify-content: space-between;
	margin-bottom: 1.25rem;
}

h1 {
	color: rgb(23 23 23 / 0.9);
	font-size: clamp(1.75rem, 4vw, 3rem);
	font-weight: 800;
	letter-spacing: 0;
	line-height: 1.05;
	margin: 0;
}

:global(.dark) h1 {
	color: rgb(255 255 255 / 0.92);
}

p {
	color: rgb(23 23 23 / 0.55);
	font-weight: 600;
	margin: 0.35rem 0 0;
}

:global(.dark) p {
	color: rgb(255 255 255 / 0.58);
}

.toggle {
	border-radius: 0.5rem;
	font-weight: 800;
	height: 2.75rem;
	padding: 0 1rem;
	white-space: nowrap;
}

.stage {
	border-top: 1px solid var(--line-divider);
	color: rgb(23 23 23 / 0.78);
	font-family: Roboto, Arial, sans-serif;
	font-size: 1.03rem;
	font-weight: 500;
	letter-spacing: 0;
	line-height: 28px;
	min-height: 280px;
	overflow: hidden;
	padding-top: 0.25rem;
	position: relative;
}

:global(.dark) .stage {
	color: rgb(255 255 255 / 0.78);
}

.line {
	left: 0;
	position: absolute;
	top: 0.25rem;
	white-space: pre;
	will-change: transform;
}

.obstacle {
	align-items: center;
	background:
		linear-gradient(135deg, rgb(38 166 154 / 0.22), rgb(46 125 50 / 0.12)),
		var(--btn-regular-bg);
	border: 1px solid rgb(38 166 154 / 0.28);
	border-radius: 0.5rem;
	box-shadow: inset 0 0 0 1px rgb(255 255 255 / 0.22);
	display: flex;
	justify-content: center;
	position: absolute;
	right: 0;
	z-index: 1;
}

.obstacle.left {
	left: 0;
	right: auto;
}

.obstacle span {
	color: var(--btn-content);
	font-size: 0.78rem;
	font-weight: 800;
	letter-spacing: 0;
	text-transform: uppercase;
}

@media (max-width: 640px) {
	.demo-shell {
		padding: 1.1rem;
	}

	.toolbar {
		align-items: flex-start;
		flex-direction: column;
	}

	.toggle {
		width: 100%;
	}

	.stage {
		font-size: 0.98rem;
	}
}
</style>
