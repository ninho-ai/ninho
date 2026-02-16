# Ninho Website

The website for [ninho.ai](https://ninho.ai).

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Hosting**: Vercel
- **Domain**: ninho.ai

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Deployment

The site is automatically deployed to Vercel on push to main.

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Custom Domain

1. Go to Vercel Dashboard > Project Settings > Domains
2. Add `ninho.ai`
3. Configure DNS at your registrar:
   - **A Record**: `@` -> `76.76.21.21`
   - **CNAME**: `www` -> `cname.vercel-dns.com`

## Structure

```
website/
├── app/
│   ├── page.tsx           # Landing page
│   ├── layout.tsx         # Root layout with metadata
│   ├── globals.css        # Tailwind styles
│   ├── sitemap.ts         # Dynamic sitemap
│   ├── docs/
│   │   └── page.tsx       # Documentation
│   └── blog/
│       ├── page.tsx       # Blog index
│       └── [slug]/        # Blog articles
├── public/
│   ├── robots.txt
│   └── og-image.png       # Open Graph image
├── next.config.js
├── tailwind.config.js
└── vercel.json
```

## Adding Blog Articles

1. Create a new directory in `app/blog/[slug]/`
2. Add a `page.tsx` with article content
3. Update the articles array in `app/blog/page.tsx`
4. Add to `app/sitemap.ts`

## SEO

- Meta tags configured in `layout.tsx`
- JSON-LD structured data for SoftwareApplication
- Open Graph and Twitter cards
- Sitemap at `/sitemap.xml`
- robots.txt configured

## Content Strategy

See the main plan for the 13-week article publishing schedule:
- Tier 1: Problem/Solution articles
- Tier 2: Tool comparisons
- Tier 3: Team/Enterprise use cases
- Tier 4: Methodology guides
- Tier 5: Technical deep-dives
