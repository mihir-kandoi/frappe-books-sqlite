import fs from 'node:fs';
import frappeUIPreset, { content as frappeUIContent } from 'frappe-ui/tailwind';
import tailwindRtl from 'tailwindcss-rtl';

const colors = JSON.parse(
  fs.readFileSync(new URL('./colors.json', import.meta.url), {
    encoding: 'utf-8',
  })
);

const colorNames =
  'gray|red|orange|yellow|green|teal|blue|indigo|purple|pink|violet|cyan|amber';
const colorSteps = '25|50|100|200|300|400|500|600|700|800|850|875|890|900';

export default {
  presets: [frappeUIPreset],
  content: [
    ...frappeUIContent,
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './templates/**/*.html',
    '../frappe_books/data/**/*.html',
  ],
  darkMode: 'class',
  safelist: [
    {
      pattern: new RegExp(`^(bg|text|border)-(${colorNames})-(${colorSteps})$`),
      variants: ['dark', 'hover', 'focus', 'focus-within', 'group-hover'],
    },
    'text-start',
    'text-center',
    'text-end',
  ],
  theme: {
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
    },
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    fontSize: {
      xs: '11px',
      sm: '12px',
      base: '13px',
      lg: '14px',
      xl: '18px',
      '2xl': '20px',
      '3xl': '24px',
      '4xl': '28px',
    },
    extend: {
      colors,
      maxHeight: {
        64: '16rem',
      },
      minWidth: {
        40: '10rem',
        56: '14rem',
      },
      maxWidth: {
        32: '8rem',
        56: '14rem',
      },
      spacing: {
        7: '1.75rem',
        14: '3.5rem',
        18: '4.5rem',
        28: '7rem',
        72: '18rem',
        80: '20rem',
      },
      boxShadow: {
        'outline-px': '0 0 0 1px rgba(66, 153, 225, 0.5)',
        DEFAULT: '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        md: '0 0 2px 0 rgba(0, 0, 0, 0.10), 0 2px 4px 0 rgba(0, 0, 0, 0.08)',
        button: '0 0.5px 0 0 rgba(0, 0, 0, 0.08)',
      },
      borderRadius: {
        sm: '0.25rem',
        DEFAULT: '0.313rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
      },
      gridColumn: {
        'span-full': '1 / -1',
      },
    },
  },
  plugins: [tailwindRtl],
};
