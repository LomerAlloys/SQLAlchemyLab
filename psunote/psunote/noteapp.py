import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()

    # for note in notes:
    #     print(note.title)

    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/edit/<note_id>",  methods=["GET", "POST"])
def notes_edit(note_id):
    print(note_id)
    
    db = models.db
    # Query to get the specific note by its ID
    note = db.session.execute(
        db.select(models.Note).filter_by(id=note_id)
    ).scalar_one_or_none()

    if note is None:
        return "Note not found", 404

    # Print the note in the terminal
    print(f"Note ID: {note.id}, Title: {note.title}, tags : {note.tags}")
    print(note)

    form = forms.NoteForm()

    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-edit.html",
            form=form,
            note=note,
        )
    form.populate_obj(note)
    note.tags = note.tags

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    print(tag_name)
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )


@app.route("/delete_note/<int:note_id>", methods=["GET", "POST"])
def delete_note(note_id):
    print("Delete pressed")
    db = models.db
    # Retrieve the note from the database
    note = db.session.execute(
        db.select(models.Note).filter_by(id=note_id)
    ).scalar_one_or_none()

    if note is None:
        return "Note not found", 404

    # Mark the note for deletion
    db.session.delete(note)
    db.session.commit()  # Commit the transaction to delete the note

    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
