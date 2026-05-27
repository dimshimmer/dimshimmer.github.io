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
	column: "left" | "right";
};

type Rect = {
	x: number;
	y: number;
	width: number;
	height: number;
};

type DragState = {
	pointerId: number;
	offsetX: number;
	offsetY: number;
} | null;

const copy =
	"Pretext gives application code direct control over line breaking. Instead of asking the browser to flow this paragraph, the demo prepares the text once, then walks one line at a time with a different width for every row. Drag the glass panel through the spread: each text band is clipped against the panel, and the next line is measured into the widest available slot. The same stream contains English, 中文排版, punctuation, and emoji-safe measurement, so the layout reacts immediately without a DOM measurement loop.";

let spread: HTMLDivElement;
let lines: PositionedLine[] = [];
let prepared: PreparedTextWithSegments | null = null;
let preparedFont = "";
let lineHeight = 30;
let spreadHeight = 560;
let panel: Rect = { x: 344, y: 138, width: 240, height: 154 };
let drag: DragState = null;
let observer: ResizeObserver | null = null;
let animationFrame = 0;

const padding = 30;
const columnGap = 34;
const panelPaddingX = 22;
const panelPaddingY = 14;

const makeFont = (style: CSSStyleDeclaration): string =>
	[
		style.fontStyle,
		style.fontVariant,
		style.fontWeight,
		style.fontSize,
		style.fontFamily,
	].join(" ");

const clamp = (value: number, min: number, max: number): number =>
	Math.max(min, Math.min(max, value));

const intersectsY = (lineTop: number, lineBottom: number, rect: Rect): boolean =>
	lineBottom > rect.y - panelPaddingY && lineTop < rect.y + rect.height + panelPaddingY;

const getColumnRegions = (containerWidth: number): Rect[] => {
	const innerWidth = containerWidth - padding * 2;
	if (innerWidth < 620) {
		return [
			{
				x: padding,
				y: 0,
				width: innerWidth,
				height: spreadHeight,
			},
		];
	}

	const columnWidth = Math.floor((innerWidth - columnGap) / 2);
	return [
		{ x: padding, y: 0, width: columnWidth, height: spreadHeight },
		{
			x: padding + columnWidth + columnGap,
			y: 0,
			width: columnWidth,
			height: spreadHeight,
		},
	];
};

const getSlotsForLine = (column: Rect, lineTop: number, lineBottom: number): Rect[] => {
	if (!intersectsY(lineTop, lineBottom, panel)) return [column];

	const blockedLeft = panel.x - panelPaddingX;
	const blockedRight = panel.x + panel.width + panelPaddingX;
	const columnLeft = column.x;
	const columnRight = column.x + column.width;
	const overlapLeft = Math.max(columnLeft, blockedLeft);
	const overlapRight = Math.min(columnRight, blockedRight);
	if (overlapRight <= overlapLeft) return [column];

	const slots: Rect[] = [];
	const leftWidth = overlapLeft - columnLeft;
	const rightWidth = columnRight - overlapRight;
	if (leftWidth >= 92) {
		slots.push({ ...column, width: leftWidth });
	}
	if (rightWidth >= 92) {
		slots.push({
			...column,
			x: overlapRight,
			width: rightWidth,
		});
	}

	if (slots.length === 0) return [];
	slots.sort((a, b) => b.width - a.width);
	return slots;
};

const layoutColumn = (
	column: Rect,
	startCursor: LayoutCursor,
	columnName: "left" | "right",
): LayoutCursor => {
	if (prepared === null) return startCursor;

	const cursor: LayoutCursor = {
		segmentIndex: startCursor.segmentIndex,
		graphemeIndex: startCursor.graphemeIndex,
	};
	let y = column.y;

	while (y + lineHeight <= column.y + column.height) {
		const slots = getSlotsForLine(column, y, y + lineHeight);
		if (slots.length === 0) {
			y += lineHeight;
			continue;
		}

		const slot = slots[0]!;
		const line = layoutNextLine(prepared, cursor, slot.width);
		if (line === null) break;

		lines = [
			...lines,
			{
				x: Math.round(slot.x),
				y: Math.round(y),
				text: line.text,
				width: line.width,
				column: columnName,
			},
		];

		cursor.segmentIndex = line.end.segmentIndex;
		cursor.graphemeIndex = line.end.graphemeIndex;
		y += lineHeight;
	}

	return cursor;
};

const layoutDemo = (): void => {
	if (!spread) return;

	const width = Math.floor(spread.clientWidth);
	if (width <= 0) return;

	const style = getComputedStyle(spread);
	const font = makeFont(style);
	const nextLineHeight = Number.parseFloat(style.lineHeight);
	if (!Number.isFinite(nextLineHeight)) return;

	if (prepared === null || preparedFont !== font) {
		prepared = prepareWithSegments(copy, font, { wordBreak: "keep-all" });
		preparedFont = font;
	}

	lineHeight = nextLineHeight;
	lines = [];

	const regions = getColumnRegions(width);
	const start: LayoutCursor = { segmentIndex: 0, graphemeIndex: 0 };
	const afterLeft = layoutColumn(regions[0]!, start, "left");
	if (regions.length > 1) {
		layoutColumn(regions[1]!, afterLeft, "right");
	}
};

const scheduleLayout = (): void => {
	if (animationFrame !== 0) return;

	animationFrame = requestAnimationFrame(() => {
		animationFrame = 0;
		layoutDemo();
	});
};

const resetPanel = (): void => {
	if (!spread) return;

	const width = spread.clientWidth;
	panel = {
		x: Math.round(width / 2 - 120),
		y: 138,
		width: 240,
		height: 154,
	};
	scheduleLayout();
};

const onPointerDown = (event: PointerEvent): void => {
	const target = event.currentTarget;
	if (!(target instanceof HTMLElement)) return;

	target.setPointerCapture(event.pointerId);
	drag = {
		pointerId: event.pointerId,
		offsetX: event.clientX - panel.x,
		offsetY: event.clientY - panel.y,
	};
};

const onPointerMove = (event: PointerEvent): void => {
	if (drag === null || drag.pointerId !== event.pointerId || !spread) return;

	const rect = spread.getBoundingClientRect();
	const nextX = event.clientX - rect.left - drag.offsetX;
	const nextY = event.clientY - rect.top - drag.offsetY;
	panel = {
		...panel,
		x: Math.round(clamp(nextX, padding, rect.width - padding - panel.width)),
		y: Math.round(clamp(nextY, 28, spreadHeight - panel.height - 28)),
	};
	scheduleLayout();
};

const onPointerUp = (event: PointerEvent): void => {
	if (drag?.pointerId !== event.pointerId) return;
	drag = null;
};

onMount(() => {
	const start = async (): Promise<void> => {
		await document.fonts?.ready;
		resetPanel();

		observer = new ResizeObserver(() => {
			resetPanel();
		});
		observer.observe(spread);
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
			<p class="eyebrow">Manual text layout</p>
			<h1>Pretext obstacle routing</h1>
		</div>
		<button type="button" class="btn-regular reset" on:click={resetPanel}>
			Reset
		</button>
	</div>

	<div
		bind:this={spread}
		class="spread"
		style={`height: ${spreadHeight}px`}
		aria-label={copy}
	>
		<p class="sr-only">{copy}</p>

		<div
			class="glass-panel"
			class:dragging={drag !== null}
			style={`transform: translate(${panel.x}px, ${panel.y}px); width: ${panel.width}px; height: ${panel.height}px`}
			on:pointerdown={onPointerDown}
			on:pointermove={onPointerMove}
			on:pointerup={onPointerUp}
			on:pointercancel={onPointerUp}
			role="button"
			tabindex="0"
			aria-label="Drag obstacle"
		>
			<span>drag me</span>
			<strong>{lines.length}</strong>
			<small>lines routed</small>
		</div>

		<div class="center-rule" aria-hidden="true"></div>

		{#each lines as line}
			<span
				class={`line line-${line.column}`}
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
	overflow: hidden;
	padding: 1.25rem;
}

.toolbar {
	align-items: center;
	display: flex;
	gap: 1rem;
	justify-content: space-between;
	padding: 0.35rem 0.25rem 1rem;
}

.eyebrow {
	color: var(--primary);
	font-size: 0.78rem;
	font-weight: 800;
	letter-spacing: 0.08em;
	margin: 0 0 0.35rem;
	text-transform: uppercase;
}

h1 {
	color: rgb(23 23 23 / 0.9);
	font-size: clamp(1.8rem, 4vw, 3.5rem);
	font-weight: 850;
	letter-spacing: 0;
	line-height: 1;
	margin: 0;
}

:global(.dark) h1 {
	color: rgb(255 255 255 / 0.92);
}

.reset {
	border-radius: 0.5rem;
	font-weight: 800;
	height: 2.75rem;
	padding: 0 1rem;
}

.spread {
	background:
		linear-gradient(to right, rgb(0 0 0 / 0.035) 1px, transparent 1px),
		linear-gradient(to bottom, rgb(0 0 0 / 0.035) 1px, transparent 1px),
		linear-gradient(135deg, rgb(38 166 154 / 0.08), transparent 42%),
		rgb(0 0 0 / 0.025);
	background-size: 30px 30px, 30px 30px, 100% 100%, 100% 100%;
	border: 1px solid rgb(0 0 0 / 0.08);
	border-radius: 0.75rem;
	color: rgb(23 23 23 / 0.78);
	font-family: Roboto, Arial, sans-serif;
	font-size: 1.02rem;
	font-weight: 500;
	letter-spacing: 0;
	line-height: 30px;
	min-height: 520px;
	overflow: hidden;
	position: relative;
	touch-action: none;
}

:global(.dark) .spread {
	background:
		linear-gradient(to right, rgb(255 255 255 / 0.045) 1px, transparent 1px),
		linear-gradient(to bottom, rgb(255 255 255 / 0.045) 1px, transparent 1px),
		linear-gradient(135deg, rgb(38 166 154 / 0.09), transparent 42%),
		rgb(255 255 255 / 0.035);
	border-color: rgb(255 255 255 / 0.1);
	color: rgb(255 255 255 / 0.78);
}

.center-rule {
	background: var(--line-divider);
	bottom: 28px;
	left: 50%;
	position: absolute;
	top: 28px;
	width: 1px;
}

.line {
	left: 0;
	position: absolute;
	top: 28px;
	white-space: pre;
	will-change: transform;
}

.line-right {
	color: rgb(23 23 23 / 0.68);
}

:global(.dark) .line-right {
	color: rgb(255 255 255 / 0.68);
}

.glass-panel {
	align-items: center;
	background:
		linear-gradient(135deg, rgb(255 255 255 / 0.72), rgb(255 255 255 / 0.34)),
		linear-gradient(135deg, rgb(38 166 154 / 0.28), rgb(27 94 32 / 0.16));
	border: 1px solid rgb(38 166 154 / 0.35);
	border-radius: 0.75rem;
	box-shadow: 0 18px 45px rgb(0 0 0 / 0.16), inset 0 1px 0 rgb(255 255 255 / 0.5);
	cursor: grab;
	display: flex;
	flex-direction: column;
	justify-content: center;
	left: 0;
	position: absolute;
	top: 0;
	user-select: none;
	will-change: transform;
	z-index: 3;
}

:global(.dark) .glass-panel {
	background:
		linear-gradient(135deg, rgb(255 255 255 / 0.16), rgb(255 255 255 / 0.07)),
		linear-gradient(135deg, rgb(38 166 154 / 0.24), rgb(76 175 80 / 0.1));
	box-shadow: 0 18px 45px rgb(0 0 0 / 0.32), inset 0 1px 0 rgb(255 255 255 / 0.15);
}

.glass-panel.dragging {
	cursor: grabbing;
}

.glass-panel span {
	color: var(--primary);
	font-size: 0.75rem;
	font-weight: 900;
	letter-spacing: 0.08em;
	text-transform: uppercase;
}

.glass-panel strong {
	color: rgb(23 23 23 / 0.84);
	font-size: 3.25rem;
	line-height: 1;
	margin-top: 0.15rem;
}

:global(.dark) .glass-panel strong {
	color: rgb(255 255 255 / 0.88);
}

.glass-panel small {
	color: rgb(23 23 23 / 0.52);
	font-weight: 800;
	margin-top: 0.25rem;
}

:global(.dark) .glass-panel small {
	color: rgb(255 255 255 / 0.56);
}

@media (max-width: 700px) {
	.demo-shell {
		padding: 1rem;
	}

	.toolbar {
		align-items: flex-start;
		flex-direction: column;
	}

	.reset {
		width: 100%;
	}

	.center-rule {
		display: none;
	}

	.spread {
		font-size: 0.96rem;
	}
}
</style>
