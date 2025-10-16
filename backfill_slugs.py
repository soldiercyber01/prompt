from app import app
from extensions import db
from models import Category, Prompt, slugify, generate_unique_slug


def backfill_categories():
    updated = 0
    with app.app_context():
        categories = Category.query.all()
        for c in categories:
            if not c.slug:
                base = slugify(c.name)
                c.slug = generate_unique_slug(db.session, Category, base, instance_id=c.id)
                updated += 1
        if updated:
            db.session.commit()
    print(f"Categories updated: {updated}")


def backfill_prompts():
    updated = 0
    with app.app_context():
        prompts = Prompt.query.all()
        for p in prompts:
            if not p.slug:
                base = slugify(p.title)
                p.slug = generate_unique_slug(db.session, Prompt, base, instance_id=p.id)
                updated += 1
        if updated:
            db.session.commit()
    print(f"Prompts updated: {updated}")


if __name__ == "__main__":
    backfill_categories()
    backfill_prompts()


