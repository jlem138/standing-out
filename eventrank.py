@admin.route('/events/edit/<leaguename>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(leaguename, id):
    """
    Edit a event
    """

    add_event = False

    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        #event.id = form.id.data
        event.day = form.day.data
        event.winner = form.winner.data
        event.loser = form.loser.data
        event.winning_score = form.winning_score.data

        event.losing_score = form.losing_score.data

        # If winner and loser are different teams, and score isn't the same
        if (event.winner != event.loser and int(event.winning_score) > int(event.losing_score)):
            try:
                db.session.commit()
                flash('You have successfully edited the event.')

            except:
                flash('The information you have entered is not correct')

            return redirect(url_for('admin.list_events', leaguename=leaguename))

        else:
            #flash('The winning and losing team you entered were the same')
            #return redirect(url_for('admin.edit_event', id=id, leaguename=leaguename))

        # redirect to the events page
            return render_template('admin/events/event.html', action="Edit",
                               add_event=add_event, form=form, leaguename=leaguename,
                               event=event, title="Edit Game Result")
    #form.id.data = event.id
    form.day.data = event.day
    form.winner.data = event.winner
    form.loser.data = event.loser
    form.winning_score.data = event.winning_score
    form.losing_score.data = event.losing_score

    return render_template('admin/events/event.html', action="Edit",
                           add_event=add_event, form=form, leaguename=leaguename,
                           event=event, title="Edit Game Result")
